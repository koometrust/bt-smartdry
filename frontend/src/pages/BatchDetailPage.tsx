import React from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';
import { api } from '../api/client';
import { PredictionBadge } from '../components/PredictionBadge';
import { AdvisoryCard } from '../components/AdvisoryCard';
import { SensorChart } from '../components/SensorChart';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  ArrowLeft,
  CheckCircle,
  Thermometer,
  RefreshCw,
} from 'lucide-react';

export const BatchDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { t } = useTranslation();
  const queryClient = useQueryClient();

  if (!id) {
    return <div>Invalid Batch ID</div>;
  }

  // Load batch details
  const {
    data: batch,
    isLoading: batchLoading,
    refetch: refetchBatch,
    isRefetching,
  } = useQuery({
    queryKey: ['batch', id],
    queryFn: () => api.getBatch(id),
    refetchInterval: 30000,
  });

  // Load batch sensor readings
  const { data: readings = [], refetch: refetchReadings } = useQuery({
    queryKey: ['readings', id],
    queryFn: () => api.getBatchReadings(id),
    refetchInterval: 30000,
  });

  // Complete batch mutation
  const completeMutation = useMutation({
    mutationFn: () => api.updateBatch(id, { status: 'completed' }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['batch', id] });
      queryClient.invalidateQueries({ queryKey: ['batches'] });
      navigate('/');
    },
  });

  if (batchLoading || !batch) {
    return (
      <div className="flex h-64 items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-brand-600 border-r-transparent"></div>
      </div>
    );
  }

  const latestReading = readings.length > 0 ? readings[readings.length - 1] : null;
  const remHours = batch.predicted_remaining_hours ?? 0;
  const h = Math.floor(remHours);
  const m = Math.round((remHours - h) * 60);

  // Calculate elapsed time from start_time
  const startTime = new Date(batch.start_time);
  const nowTime = new Date();
  const elapsedMinutes = Math.max(0, Math.round((nowTime.getTime() - startTime.getTime()) / 60000));
  const elapsedH = Math.floor(elapsedMinutes / 60);
  const elapsedM = elapsedMinutes % 60;

  return (
    <div className="space-y-6">
      {/* Top Navigation & Status Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div className="flex items-center space-x-3">
          <Button asChild variant="outline" size="icon">
            <Link to="/">
              <ArrowLeft className="w-5 h-5" />
            </Link>
          </Button>
          <div>
            <div className="flex items-center space-x-2">
              <Badge variant="secondary" className="text-brand-700 bg-brand-50">
                {batch.status === 'active' ? t('status.active') : t('status.completed')}
              </Badge>
              <span className="text-xs text-muted-foreground font-mono">ID: {batch.id.slice(0, 8)}</span>
            </div>
            <h1 className="text-2xl font-extrabold text-foreground tracking-tight mt-0.5">
              {t(`crops.${batch.crop_type.toLowerCase()}`) || batch.crop_type}
            </h1>
          </div>
        </div>

        <div className="flex items-center space-x-2.5">
          <Button
            variant="outline"
            size="icon"
            onClick={() => {
              refetchBatch();
              refetchReadings();
            }}
            title="Refresh telemetry"
          >
            <RefreshCw className={`w-4 h-4 ${isRefetching ? 'animate-spin text-brand-600' : ''}`} />
          </Button>

          {batch.status === 'active' && (
            <Button
              onClick={() => {
                if (window.confirm(t('batches.confirmComplete'))) {
                  completeMutation.mutate();
                }
              }}
              disabled={completeMutation.isPending}
              className="bg-emerald-600 hover:bg-emerald-700 text-white"
            >
              <CheckCircle className="w-4 h-4 mr-1.5" />
              {completeMutation.isPending ? t('batches.completing') : t('batches.completeBatch')}
            </Button>
          )}
        </div>
      </div>

      {/* Action Advisory Banner (Bilingual) */}
      <AdvisoryCard
        advisoryEn={batch.current_advisory_en}
        advisorySw={batch.current_advisory_sw}
      />

      {/* Key Metrics Summary Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {/* Current Moisture */}
        <Card>
          <CardContent className="p-4">
            <span className="text-xs font-bold text-muted-foreground uppercase tracking-wider block">
              {t('batches.currentMoisture')}
            </span>
            <div className="mt-2 flex items-baseline">
              <span className="text-2xl font-black text-blue-600">
                {batch.current_moisture_pct !== undefined ? `${batch.current_moisture_pct}%` : 'Pending'}
              </span>
              <span className="ml-2 text-xs font-medium text-muted-foreground">
                Target: {batch.target_moisture_pct}%
              </span>
            </div>
          </CardContent>
        </Card>

        {/* Remaining Time */}
        <Card>
          <CardContent className="p-4">
            <span className="text-xs font-bold text-muted-foreground uppercase tracking-wider block">
              {t('batches.remainingTime')}
            </span>
            <div className="mt-2 flex items-baseline">
              <span className="text-2xl font-black text-foreground">
                {remHours > 0 ? `${h}h ${m}m` : '0h 0m'}
              </span>
              <span className="ml-2 text-xs font-medium text-muted-foreground">
                Elapsed: {elapsedH}h {elapsedM}m
              </span>
            </div>
          </CardContent>
        </Card>

        {/* Predicted Grade */}
        <Card>
          <CardContent className="p-4">
            <span className="text-xs font-bold text-muted-foreground uppercase tracking-wider block">
              {t('batches.predictedGrade')}
            </span>
            <div className="mt-2">
              <PredictionBadge grade={batch.predicted_quality_grade} size="md" />
            </div>
          </CardContent>
        </Card>

        {/* Harvest Weight */}
        <Card>
          <CardContent className="p-4">
            <span className="text-xs font-bold text-muted-foreground uppercase tracking-wider block">
              {t('batches.initialWeight')}
            </span>
            <div className="mt-2 flex items-baseline">
              <span className="text-2xl font-black text-foreground">{batch.initial_weight_kg} kg</span>
              <span className="ml-2 text-xs font-medium text-muted-foreground">Solar Tray</span>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Live Telemetry Chart */}
      <SensorChart readings={readings} targetMoisturePct={batch.target_moisture_pct} />

      {/* Latest Sensor Snapshot Card */}
      {latestReading && (
        <Card>
          <CardHeader className="p-5 pb-3">
            <CardTitle className="text-sm font-bold text-foreground flex items-center">
              <Thermometer className="w-4 h-4 mr-1.5 text-brand-600" />
              {t('detail.sensorStatus')}
            </CardTitle>
          </CardHeader>
          <CardContent className="p-5 pt-0">
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 text-center">
              <div className="p-3 bg-red-50 rounded-lg">
                <span className="text-[10px] font-bold text-red-600 uppercase">Dryer Temp</span>
                <p className="text-lg font-black text-red-900">{latestReading.temperature}°C</p>
              </div>
              <div className="p-3 bg-cyan-50 rounded-lg">
                <span className="text-[10px] font-bold text-cyan-600 uppercase">Dryer Humidity</span>
                <p className="text-lg font-black text-cyan-900">{latestReading.humidity}%</p>
              </div>
              <div className="p-3 bg-purple-50 rounded-lg">
                <span className="text-[10px] font-bold text-purple-600 uppercase">VPD Deficit</span>
                <p className="text-lg font-black text-purple-900">{latestReading.vpd} kPa</p>
              </div>
              <div className="p-3 bg-amber-50 rounded-lg">
                <span className="text-[10px] font-bold text-amber-600 uppercase">Ambient Temp</span>
                <p className="text-lg font-black text-amber-900">{latestReading.ambient_temperature}°C</p>
              </div>
              <div className="p-3 bg-sky-50 rounded-lg">
                <span className="text-[10px] font-bold text-sky-600 uppercase">Ambient Humidity</span>
                <p className="text-lg font-black text-sky-900">{latestReading.ambient_humidity}%</p>
              </div>
              <div className="p-3 bg-blue-50 rounded-lg">
                <span className="text-[10px] font-bold text-blue-600 uppercase">Current Moisture</span>
                <p className="text-lg font-black text-blue-900">{latestReading.current_moisture}%</p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};
