import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../context/AuthContext';
import { api } from '../api/client';
import { PredictionBadge } from '../components/PredictionBadge';
import { CapacityMeter } from '../components/CapacityMeter';
import { CreateBatchModal } from '../components/CreateBatchModal';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import {
  Layers,
  Plus,
  Clock,
  Droplets,
  ArrowRight,
  CheckCircle,
  Building2,
  RefreshCw,
} from 'lucide-react';

export const ActiveBatchesPage: React.FC = () => {
  const { user, isAdmin } = useAuth();
  const { t } = useTranslation();
  const queryClient = useQueryClient();

  const [selectedHubId, setSelectedHubId] = useState<string>('');
  const [modalOpen, setModalOpen] = useState(false);

  // Load hubs
  const { data: hubs = [] } = useQuery({
    queryKey: ['hubs'],
    queryFn: () => api.getHubs(),
  });

  // Effective hub id for operator vs admin
  const effectiveHubId = isAdmin
    ? selectedHubId || undefined
    : user?.hub_id || undefined;

  // Load active batches with 30s polling
  const {
    data: batches = [],
    isLoading,
    isRefetching,
    refetch,
  } = useQuery({
    queryKey: ['batches', 'active', effectiveHubId],
    queryFn: () => api.getBatches('active', effectiveHubId),
    refetchInterval: 30000,
  });

  // Create Batch Mutation
  const createMutation = useMutation({
    mutationFn: (data: {
      hub_id: string;
      crop_type: string;
      initial_weight_kg: number;
      target_moisture_pct?: number;
    }) => api.createBatch(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['batches'] });
    },
  });

  // Complete Batch Mutation
  const completeMutation = useMutation({
    mutationFn: (id: string) => api.updateBatch(id, { status: 'completed' }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['batches'] });
    },
  });

  // Calculate current loaded weight in the selected hub for capacity check
  const currentLoadedWeight = batches.reduce(
    (acc, b) => acc + (b.initial_weight_kg || 0),
    0
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="sm:flex sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-extrabold text-foreground tracking-tight flex items-center">
            <Layers className="w-6 h-6 mr-2.5 text-brand-600" />
            {t('batches.title')}
          </h1>
          <p className="mt-1 text-sm text-muted-foreground">{t('batches.subtitle')}</p>
        </div>
        <div className="mt-4 sm:mt-0 flex items-center space-x-2.5">
          <Button
            variant="outline"
            size="icon"
            onClick={() => refetch()}
            title="Refresh now"
          >
            <RefreshCw className={`w-4 h-4 ${isRefetching ? 'animate-spin text-brand-600' : ''}`} />
          </Button>
          <Button
            variant="brand"
            onClick={() => setModalOpen(true)}
          >
            <Plus className="w-4 h-4 mr-1.5" />
            {t('batches.createNew')}
          </Button>
        </div>
      </div>

      {/* Admin Hub Filter Tabs */}
      {isAdmin && hubs.length > 0 && (
        <div className="flex items-center space-x-1.5 overflow-x-auto pb-1 border-b border-border">
          <Button
            variant={selectedHubId === '' ? 'brand' : 'outline'}
            size="sm"
            onClick={() => setSelectedHubId('')}
          >
            {t('batches.allHubs')}
          </Button>
          {hubs.map((hub) => (
            <Button
              key={hub.id}
              variant={selectedHubId === hub.id ? 'brand' : 'outline'}
              size="sm"
              onClick={() => setSelectedHubId(hub.id)}
            >
              <Building2 className="w-3.5 h-3.5 mr-1" />
              {hub.name}
            </Button>
          ))}
        </div>
      )}

      {/* Hub Dryer Capacity Meter banner (per ADR-0002) */}
      <Card>
        <CardContent className="p-4">
          <div className="sm:flex sm:items-center sm:justify-between mb-2">
            <div className="text-xs font-bold text-muted-foreground uppercase tracking-wider">
              Dryer Capacity Utilization (200 kg Max)
            </div>
            <div className="text-xs text-muted-foreground">
              {batches.length} active batch{batches.length !== 1 ? 'es' : ''} currently drying
            </div>
          </div>
          <CapacityMeter currentWeightKg={currentLoadedWeight} maxCapacityKg={200} />
        </CardContent>
      </Card>

      {/* Batches Grid */}
      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {[1, 2, 3].map((i) => (
            <Card key={i} className="h-64 animate-pulse" />
          ))}
        </div>
      ) : batches.length === 0 ? (
        <Card className="border-dashed p-12 text-center">
          <Layers className="w-12 h-12 text-muted mx-auto mb-3" />
          <h3 className="text-base font-bold text-foreground">{t('batches.noActive')}</h3>
          <p className="mt-1 text-sm text-muted-foreground">
            Click &quot;New Batch&quot; or start the simulator to feed real-time drying data.
          </p>
          <Button
            variant="brand"
            onClick={() => setModalOpen(true)}
            className="mt-4 inline-flex"
          >
            <Plus className="w-4 h-4 mr-1.5" />
            {t('batches.createNew')}
          </Button>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {batches.map((batch) => {
            const cropName =
              t(`crops.${batch.crop_type.toLowerCase()}`) || batch.crop_type;
            const hub = hubs.find((h) => h.id === batch.hub_id);

            // Remaining hours formatting
            const remHours = batch.predicted_remaining_hours ?? 0;
            const h = Math.floor(remHours);
            const m = Math.round((remHours - h) * 60);

            // Moisture progress estimate
            const currM = batch.current_moisture_pct ?? 75;
            const targetM = batch.target_moisture_pct;
            const moistureProgress = Math.min(
              100,
              Math.max(0, Math.round(((75 - currM) / (75 - targetM)) * 100))
            );

            return (
              <Card
                key={batch.id}
                className="hover:shadow-md transition-shadow flex flex-col justify-between"
              >
                <CardHeader className="p-5 pb-3">
                  <div className="flex justify-between items-start">
                    <div>
                      <Badge variant="secondary" className="mb-1 text-brand-700 bg-brand-50">
                        {hub?.name || 'Solar Dryer'}
                      </Badge>
                      <CardTitle className="text-lg font-bold text-foreground mt-1">
                        {cropName}
                      </CardTitle>
                    </div>
                    <PredictionBadge grade={batch.predicted_quality_grade} size="sm" />
                  </div>
                </CardHeader>

                <CardContent className="p-5 pt-0">
                  {/* Weight and moisture metric row */}
                  <div className="grid grid-cols-2 gap-2 my-3 p-3 bg-muted/50 rounded-xl text-center">
                    <div>
                      <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider block">
                        {t('batches.initialWeight')}
                      </span>
                      <span className="text-base font-extrabold text-foreground">
                        {batch.initial_weight_kg} kg
                      </span>
                    </div>
                    <div>
                      <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider block">
                        {t('batches.currentMoisture')}
                      </span>
                      <span className="text-base font-extrabold text-blue-600 flex items-center justify-center">
                        <Droplets className="w-4 h-4 mr-0.5 text-blue-500" />
                        {batch.current_moisture_pct !== undefined
                          ? `${batch.current_moisture_pct}%`
                          : 'Pending'}
                      </span>
                    </div>
                  </div>

                  {/* Moisture Progress Bar */}
                  <div className="mb-4">
                    <div className="flex justify-between text-xs text-muted-foreground mb-1.5 font-medium">
                      <span>Drying Progress</span>
                      <span>Target: {targetM}%</span>
                    </div>
                    <Progress value={moistureProgress} indicatorClassName="bg-brand-600" />
                  </div>

                  {/* Estimated remaining drying time countdown */}
                  <div className="flex items-center justify-between text-xs text-muted-foreground py-2 border-t border-border">
                    <span className="flex items-center">
                      <Clock className="w-3.5 h-3.5 mr-1" />
                      {t('batches.remainingTime')}:
                    </span>
                    <span className="font-extrabold text-foreground">
                      {remHours > 0 ? `${h}h ${m}m` : 'Target reached'}
                    </span>
                  </div>

                  {/* Bottom action buttons */}
                  <div className="mt-4 pt-3 border-t border-border flex items-center space-x-2">
                    <Button
                      asChild
                      variant="secondary"
                      size="sm"
                      className="flex-1 font-bold text-brand-700 bg-brand-50 hover:bg-brand-100"
                    >
                      <Link to={`/batches/${batch.id}`}>
                        {t('batches.viewDetails')}
                        <ArrowRight className="w-3.5 h-3.5 ml-1" />
                      </Link>
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => {
                        if (window.confirm(t('batches.confirmComplete'))) {
                          completeMutation.mutate(batch.id);
                        }
                      }}
                      title={t('batches.completeBatch')}
                      className="text-muted-foreground hover:text-emerald-600 hover:bg-emerald-50"
                    >
                      <CheckCircle className="w-5 h-5" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}

      {/* Modal for creating batch */}
      <CreateBatchModal
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        onSubmit={async (data) => {
          await createMutation.mutateAsync(data);
        }}
        hubs={hubs}
        defaultHubId={effectiveHubId}
        currentLoadedWeight={currentLoadedWeight}
      />
    </div>
  );
};
