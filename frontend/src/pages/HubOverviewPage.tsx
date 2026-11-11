import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { api } from '../api/client';
import { CapacityMeter } from '../components/CapacityMeter';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Building2,
  MapPin,
  ArrowRight,
  Sun,
  CheckCircle2,
} from 'lucide-react';

export const HubOverviewPage: React.FC = () => {
  const { t } = useTranslation();

  // Load hubs
  const { data: hubs = [], isLoading: hubsLoading } = useQuery({
    queryKey: ['hubs'],
    queryFn: () => api.getHubs(),
  });

  // Load all active batches to compute per-hub capacity utilization
  const { data: activeBatches = [], isLoading: batchesLoading } = useQuery({
    queryKey: ['batches', 'active'],
    queryFn: () => api.getBatches('active'),
  });

  const isLoading = hubsLoading || batchesLoading;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-extrabold text-foreground tracking-tight flex items-center">
          <Building2 className="w-6 h-6 mr-2.5 text-brand-600" />
          {t('hubs.title')}
        </h1>
        <p className="mt-1 text-sm text-muted-foreground">{t('hubs.subtitle')}</p>
      </div>

      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {[1, 2, 3].map((i) => (
            <Card key={i} className="h-64 animate-pulse" />
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {hubs.map((hub) => {
            // Find active batches for this hub
            const hubBatches = activeBatches.filter((b) => b.hub_id === hub.id);
            const loadedWeight = hubBatches.reduce(
              (acc, b) => acc + (b.initial_weight_kg || 0),
              0
            );
            const maxCap = hub.total_capacity_kg || 200;
            const availableKg = Math.max(0, maxCap - loadedWeight);
            const isFull = availableKg <= 0;

            let hubDesc = 'Highland agroforestry zone';
            if (hub.location.toLowerCase().includes('tharaka')) {
              hubDesc = 'Semi-arid warm solar basin';
            } else if (hub.location.toLowerCase().includes('eldoret')) {
              hubDesc = 'High-altitude Western highlands';
            }

            return (
              <Card
                key={hub.id}
                className="hover:shadow-md transition-shadow flex flex-col justify-between"
              >
                <CardHeader className="p-6 pb-2">
                  <div className="flex justify-between items-start">
                    <div>
                      <Badge variant="secondary" className="mb-1 text-brand-700 bg-brand-50">
                        <MapPin className="w-3 h-3 mr-1" />
                        {hub.location.toUpperCase()}
                      </Badge>
                      <CardTitle className="text-xl font-bold text-foreground">
                        {hub.name}
                      </CardTitle>
                      <p className="text-xs text-muted-foreground mt-0.5">{hubDesc}</p>
                    </div>
                    <div className="w-10 h-10 rounded-xl bg-solar-50 flex items-center justify-center text-solar-600">
                      <Sun className="w-6 h-6" />
                    </div>
                  </div>
                </CardHeader>

                <CardContent className="p-6 pt-2">
                  {/* Capacity Bar */}
                  <div className="my-4 p-4 bg-muted/40 rounded-xl border border-border">
                    <div className="flex justify-between items-center text-xs font-bold text-foreground mb-2">
                      <span>{t('hubs.capacityUsed')}</span>
                      <span className={isFull ? 'text-destructive font-bold' : 'text-emerald-700'}>
                        {isFull ? t('hubs.full') : t('hubs.normal')}
                      </span>
                    </div>
                    <CapacityMeter
                      currentWeightKg={loadedWeight}
                      maxCapacityKg={maxCap}
                      showLabels={true}
                    />
                  </div>

                  {/* Hub Stats */}
                  <div className="grid grid-cols-2 gap-3 mb-4 text-center">
                    <div className="p-3 bg-brand-50/60 rounded-lg">
                      <span className="text-[10px] font-bold text-brand-700 uppercase block">
                        Active Batches
                      </span>
                      <span className="text-xl font-black text-brand-900">
                        {hubBatches.length}
                      </span>
                    </div>
                    <div className="p-3 bg-blue-50/60 rounded-lg">
                      <span className="text-[10px] font-bold text-blue-700 uppercase block">
                        Available Cap.
                      </span>
                      <span className="text-xl font-black text-blue-900">
                        {availableKg} kg
                      </span>
                    </div>
                  </div>

                  {/* Operator Info */}
                  <div className="text-xs text-muted-foreground space-y-1 pt-3 border-t border-border">
                    <div className="flex items-center justify-between">
                      <span className="font-medium">Standard Tray Capacity:</span>
                      <span className="font-bold text-foreground">{maxCap} kg</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="font-medium">IoT Sensor Node:</span>
                      <span className="font-semibold text-emerald-600 flex items-center">
                        <CheckCircle2 className="w-3 h-3 mr-1" />
                        Online
                      </span>
                    </div>
                  </div>

                  <div className="mt-5 pt-4 border-t border-border">
                    <Button asChild variant="brand" className="w-full">
                      <Link to="/">
                        View Hub Active Batches
                        <ArrowRight className="w-3.5 h-3.5 ml-1.5" />
                      </Link>
                    </Button>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
};
