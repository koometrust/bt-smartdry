import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';
import { api } from '../api/client';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  BarChart3,
  Award,
  Scale,
  Layers,
  PieChart,
  Building2,
  ShieldCheck,
  TrendingUp,
  Info,
} from 'lucide-react';

export const AnalyticsPage: React.FC = () => {
  const { t } = useTranslation();

  // Load hubs
  const { data: hubs = [] } = useQuery({
    queryKey: ['hubs'],
    queryFn: () => api.getHubs(),
  });

  // Load all batches (completed and active)
  const { data: allBatches = [], isLoading } = useQuery({
    queryKey: ['batches', 'all'],
    queryFn: () => api.getBatches(),
  });

  // Load network-wide analytics overview
  const { data: analyticsOverview } = useQuery({
    queryKey: ['analytics', 'overview'],
    queryFn: () => api.getAnalyticsOverview(),
  });

  // Calculate Metrics
  const totalBatches = allBatches.length;
  const completedBatches = allBatches.filter((b) => b.status === 'completed');
  const totalWeightKg = allBatches.reduce((acc, b) => acc + (b.initial_weight_kg || 0), 0);

  const totalAvoidedLossKg =
    analyticsOverview?.total_avoided_loss_kg ??
    completedBatches.reduce((acc, b) => acc + (b.avoided_loss_kg || 0), 0);
  const totalAvoidedLossKes =
    analyticsOverview?.total_avoided_loss_kes ??
    completedBatches.reduce((acc, b) => acc + (b.avoided_loss_kes || 0), 0);

  // Quality grades breakdown
  let exportCount = 0;
  let standardCount = 0;
  let downgradedCount = 0;

  allBatches.forEach((b) => {
    const grade = (b.final_quality_grade || b.predicted_quality_grade || 'standard').toLowerCase();
    if (grade === 'export') exportCount++;
    else if (grade === 'downgraded') downgradedCount++;
    else standardCount++;
  });

  const exportRatePct = totalBatches > 0 ? Math.round((exportCount / totalBatches) * 100) : 0;

  // Crops breakdown
  const cropCounts: Record<string, { count: number; weight: number }> = {
    moringa: { count: 0, weight: 0 },
    hibiscus: { count: 0, weight: 0 },
    prunus: { count: 0, weight: 0 },
  };

  allBatches.forEach((b) => {
    const c = b.crop_type.toLowerCase();
    if (!cropCounts[c]) cropCounts[c] = { count: 0, weight: 0 };
    cropCounts[c].count++;
    cropCounts[c].weight += b.initial_weight_kg || 0;
  });

  // Comparative Hub Performance
  const hubStats = hubs.map((hub) => {
    const hubBatches = allBatches.filter((b) => b.hub_id === hub.id);
    const completed = hubBatches.filter((b) => b.status === 'completed');
    const active = hubBatches.filter((b) => b.status === 'active');
    const totalWeight = hubBatches.reduce((acc, b) => acc + (b.initial_weight_kg || 0), 0);
    const activeWeight = active.reduce((acc, b) => acc + (b.initial_weight_kg || 0), 0);
    const hubExport = hubBatches.filter(
      (b) => (b.final_quality_grade || b.predicted_quality_grade) === 'export'
    ).length;
    const exportRate = hubBatches.length > 0 ? Math.round((hubExport / hubBatches.length) * 100) : 0;

    return {
      hub,
      totalBatches: hubBatches.length,
      completedBatches: completed.length,
      activeBatches: active.length,
      totalWeight,
      activeWeight,
      exportRate,
    };
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-extrabold text-foreground tracking-tight flex items-center">
          <BarChart3 className="w-6 h-6 mr-2.5 text-brand-600" />
          {t('analytics.title')}
        </h1>
        <p className="mt-1 text-sm text-muted-foreground">{t('analytics.subtitle')}</p>
      </div>

      {isLoading ? (
        <Card className="h-64 animate-pulse" />
      ) : (
        <>
          {/* Top KPI Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <Card>
              <CardContent className="p-5">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-muted-foreground uppercase tracking-wider">
                    {t('analytics.totalBatches')}
                  </span>
                  <div className="w-8 h-8 rounded-lg bg-brand-50 text-brand-700 flex items-center justify-center">
                    <Layers className="w-4 h-4" />
                  </div>
                </div>
                <p className="mt-3 text-3xl font-black text-foreground">{totalBatches}</p>
                <p className="mt-1 text-xs text-muted-foreground">
                  {t('analytics.completedCycles', { count: completedBatches.length })}
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-5">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-muted-foreground uppercase tracking-wider">
                    {t('analytics.totalWeight')}
                  </span>
                  <div className="w-8 h-8 rounded-lg bg-blue-50 text-blue-700 flex items-center justify-center">
                    <Scale className="w-4 h-4" />
                  </div>
                </div>
                <p className="mt-3 text-3xl font-black text-foreground">{totalWeightKg.toLocaleString()} kg</p>
                <p className="mt-1 text-xs text-muted-foreground">{t('analytics.acrossHubs')}</p>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-5">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-muted-foreground uppercase tracking-wider">
                    {t('analytics.exportRate')}
                  </span>
                  <div className="w-8 h-8 rounded-lg bg-emerald-50 text-emerald-700 flex items-center justify-center">
                    <Award className="w-4 h-4" />
                  </div>
                </div>
                <p className="mt-3 text-3xl font-black text-emerald-600">{exportRatePct}%</p>
                <p className="mt-1 text-xs text-emerald-700 font-medium">{t('analytics.optimalRange')}</p>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-5">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-muted-foreground uppercase tracking-wider">
                    {t('analytics.dryerCapacity')}
                  </span>
                  <div className="w-8 h-8 rounded-lg bg-purple-50 text-purple-700 flex items-center justify-center">
                    <Building2 className="w-4 h-4" />
                  </div>
                </div>
                <p className="mt-3 text-3xl font-black text-foreground">200 kg</p>
                <p className="mt-1 text-xs text-muted-foreground">{t('analytics.perDryer')}</p>
              </CardContent>
            </Card>
          </div>

          {/* Avoided Post-Harvest Loss Summary (Objective 6) */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Card className="border-emerald-200 bg-emerald-50/30">
              <CardContent className="p-5">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-emerald-900 uppercase tracking-wider">
                    {t('loss.totalPreservedKg')}
                  </span>
                  <div className="w-8 h-8 rounded-lg bg-emerald-100 text-emerald-800 flex items-center justify-center">
                    <ShieldCheck className="w-4 h-4" />
                  </div>
                </div>
                <p className="mt-3 text-3xl font-black text-emerald-700">
                  +{totalAvoidedLossKg.toLocaleString()} kg
                </p>
                <p className="mt-1 text-xs text-muted-foreground">
                  {t('loss.baselineComparison')}
                </p>
              </CardContent>
            </Card>

            <Card className="border-emerald-200 bg-emerald-50/30">
              <CardContent className="p-5">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-emerald-900 uppercase tracking-wider">
                    {t('loss.totalPreservedKes')}
                  </span>
                  <div className="w-8 h-8 rounded-lg bg-emerald-100 text-emerald-800 flex items-center justify-center">
                    <TrendingUp className="w-4 h-4" />
                  </div>
                </div>
                <p className="mt-3 text-3xl font-black text-emerald-700">
                  {totalAvoidedLossKes.toLocaleString()} KES
                </p>
                <div className="mt-1 flex items-center text-[11px] text-muted-foreground italic">
                  <Info className="w-3 h-3 mr-1 text-emerald-600 flex-shrink-0" />
                  <span>{t('loss.indicativeDisclaimer')}</span>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Charts Row: Grade Breakdown & Crop Breakdown */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Grade Distribution */}
            <Card>
              <CardHeader className="p-6 pb-2">
                <CardTitle className="text-base font-bold text-foreground flex items-center">
                  <Award className="w-4 h-4 mr-2 text-brand-600" />
                  {t('analytics.gradeDistribution')}
                </CardTitle>
              </CardHeader>

              <CardContent className="p-6 pt-2 space-y-4">
                {/* Export */}
                <div>
                  <div className="flex justify-between text-xs font-bold mb-1.5">
                    <span className="text-emerald-800">{t('grades.export')}</span>
                    <span className="text-emerald-900">
                      {exportCount} ({totalBatches > 0 ? Math.round((exportCount / totalBatches) * 100) : 0}%)
                    </span>
                  </div>
                  <Progress
                    value={totalBatches > 0 ? (exportCount / totalBatches) * 100 : 0}
                    indicatorClassName="bg-emerald-500"
                    className="h-3"
                  />
                </div>

                {/* Standard */}
                <div>
                  <div className="flex justify-between text-xs font-bold mb-1.5">
                    <span className="text-blue-800">{t('grades.standard')}</span>
                    <span className="text-blue-900">
                      {standardCount} ({totalBatches > 0 ? Math.round((standardCount / totalBatches) * 100) : 0}%)
                    </span>
                  </div>
                  <Progress
                    value={totalBatches > 0 ? (standardCount / totalBatches) * 100 : 0}
                    indicatorClassName="bg-blue-500"
                    className="h-3"
                  />
                </div>

                {/* Downgraded */}
                <div>
                  <div className="flex justify-between text-xs font-bold mb-1.5">
                    <span className="text-amber-800">{t('grades.downgraded')}</span>
                    <span className="text-amber-900">
                      {downgradedCount} ({totalBatches > 0 ? Math.round((downgradedCount / totalBatches) * 100) : 0}%)
                    </span>
                  </div>
                  <Progress
                    value={totalBatches > 0 ? (downgradedCount / totalBatches) * 100 : 0}
                    indicatorClassName="bg-amber-500"
                    className="h-3"
                  />
                </div>
              </CardContent>
            </Card>

            {/* Crop Throughput */}
            <Card>
              <CardHeader className="p-6 pb-2">
                <CardTitle className="text-base font-bold text-foreground flex items-center">
                  <PieChart className="w-4 h-4 mr-2 text-brand-600" />
                  {t('analytics.cropBreakdown')}
                </CardTitle>
              </CardHeader>

              <CardContent className="p-6 pt-2 space-y-4">
                {Object.entries(cropCounts).map(([crop, data]) => {
                  const pct = totalWeightKg > 0 ? Math.round((data.weight / totalWeightKg) * 100) : 0;
                  const label = t(`crops.${crop}`) || crop;

                  return (
                    <div key={crop}>
                      <div className="flex justify-between text-xs font-bold mb-1.5">
                        <span className="text-foreground capitalize">{label}</span>
                        <span className="text-muted-foreground font-semibold">
                          {data.weight} kg ({pct}%)
                        </span>
                      </div>
                      <Progress value={pct} indicatorClassName="bg-brand-600" className="h-3" />
                    </div>
                  );
                })}
              </CardContent>
            </Card>
          </div>

          {/* Comparative Hub Performance (per Spec) */}
          <Card>
            <CardHeader className="p-6 pb-3">
              <CardTitle className="text-base font-bold text-foreground flex items-center">
                <Building2 className="w-4 h-4 mr-2 text-brand-600" />
                {t('analytics.hubPerformance')}
              </CardTitle>
            </CardHeader>
            <CardContent className="p-6 pt-0 overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>{t('analytics.hub')}</TableHead>
                    <TableHead>{t('analytics.batchesCount')}</TableHead>
                    <TableHead>{t('analytics.weightKg')}</TableHead>
                    <TableHead>{t('analytics.exportRate')}</TableHead>
                    <TableHead>{t('analytics.activeLoad')} (200 kg)</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {hubStats.map((item) => (
                    <TableRow key={item.hub.id}>
                      <TableCell className="font-bold text-foreground">
                        <div className="flex items-center space-x-1.5">
                          <Building2 className="w-3.5 h-3.5 text-brand-600" />
                          <span>{item.hub.name}</span>
                        </div>
                        <span className="text-[11px] text-muted-foreground">{item.hub.location}</span>
                      </TableCell>
                      <TableCell className="font-medium text-foreground">
                        {item.totalBatches} ({item.activeBatches} active)
                      </TableCell>
                      <TableCell className="font-semibold text-foreground">
                        {item.totalWeight} kg
                      </TableCell>
                      <TableCell>
                        <Badge
                          variant="secondary"
                          className={
                            item.exportRate >= 80
                              ? 'bg-emerald-50 text-emerald-700 font-bold'
                              : 'bg-blue-50 text-blue-700 font-bold'
                          }
                        >
                          {item.exportRate}% Export
                        </Badge>
                      </TableCell>
                      <TableCell className="w-48">
                        <div className="flex justify-between text-xs mb-1 font-semibold">
                          <span>{item.activeWeight} kg</span>
                          <span className="text-muted-foreground">{Math.round((item.activeWeight / 200) * 100)}%</span>
                        </div>
                        <Progress
                          value={(item.activeWeight / 200) * 100}
                          indicatorClassName={item.activeWeight >= 180 ? 'bg-amber-500' : 'bg-brand-600'}
                          className="h-2"
                        />
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
};
