import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { api } from '../api/client';
import { PredictionBadge } from '../components/PredictionBadge';
import { formatBatchDuration } from '../utils/formatters';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { History, Filter, ArrowRight, Search, Building2, Clock } from 'lucide-react';

export const BatchHistoryPage: React.FC = () => {
  const { t } = useTranslation();
  const [selectedCrop, setSelectedCrop] = useState<string>('all');
  const [selectedGrade, setSelectedGrade] = useState<string>('all');
  const [selectedHub, setSelectedHub] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState<string>('');

  const { data: hubs = [] } = useQuery({
    queryKey: ['hubs'],
    queryFn: () => api.getHubs(),
  });

  const { data: batches = [], isLoading } = useQuery({
    queryKey: ['batches', 'completed'],
    queryFn: () => api.getBatches('completed'),
  });

  const filtered = batches.filter((b) => {
    if (selectedCrop !== 'all' && b.crop_type.toLowerCase() !== selectedCrop) {
      return false;
    }
    const finalGrade = (b.final_quality_grade || b.predicted_quality_grade || '').toLowerCase();
    if (selectedGrade !== 'all' && finalGrade !== selectedGrade) {
      return false;
    }
    if (selectedHub !== 'all' && b.hub_id !== selectedHub) {
      return false;
    }
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase().trim();
      const cropName = (t(`crops.${b.crop_type.toLowerCase()}`) || b.crop_type).toLowerCase();
      const hubName = (hubs.find((h) => h.id === b.hub_id)?.name || '').toLowerCase();
      const batchId = b.id.toLowerCase();
      if (!cropName.includes(q) && !hubName.includes(q) && !batchId.includes(q)) {
        return false;
      }
    }
    return true;
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="sm:flex sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-extrabold text-foreground tracking-tight flex items-center">
            <History className="w-6 h-6 mr-2.5 text-brand-600" />
            {t('history.title')}
          </h1>
          <p className="mt-1 text-sm text-muted-foreground">{t('history.subtitle')}</p>
        </div>
        <div className="mt-2 text-xs font-semibold text-muted-foreground">
          {t('history.totalCompleted', { count: batches.length })}
        </div>
      </div>

      {/* Filter and Search Toolbar */}
      <Card>
        <CardContent className="p-3.5 flex flex-wrap items-center gap-3">
          {/* Search Box */}
          <div className="relative flex-1 min-w-[200px]">
            <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder={t('history.searchPlaceholder')}
              className="w-full text-xs pl-8 pr-3 py-1.5 border border-input rounded-lg bg-background font-medium text-foreground placeholder:text-muted-foreground"
            />
          </div>

          <div className="flex items-center text-xs font-bold text-muted-foreground uppercase tracking-wider mr-1">
            <Filter className="w-3.5 h-3.5 mr-1" />
            Filter:
          </div>

          {/* Hub filter */}
          <select
            value={selectedHub}
            onChange={(e) => setSelectedHub(e.target.value)}
            className="text-xs border border-input rounded-lg py-1.5 px-2.5 bg-background font-medium text-foreground"
          >
            <option value="all">{t('history.allHubs')}</option>
            {hubs.map((hub) => (
              <option key={hub.id} value={hub.id}>
                {hub.name}
              </option>
            ))}
          </select>

          {/* Crop filter */}
          <select
            value={selectedCrop}
            onChange={(e) => setSelectedCrop(e.target.value)}
            className="text-xs border border-input rounded-lg py-1.5 px-2.5 bg-background font-medium text-foreground"
          >
            <option value="all">{t('history.allCrops')}</option>
            <option value="moringa">Moringa</option>
            <option value="hibiscus">Hibiscus</option>
            <option value="prunus">Prunus</option>
          </select>

          {/* Grade filter */}
          <select
            value={selectedGrade}
            onChange={(e) => setSelectedGrade(e.target.value)}
            className="text-xs border border-input rounded-lg py-1.5 px-2.5 bg-background font-medium text-foreground"
          >
            <option value="all">{t('history.allGrades')}</option>
            <option value="export">Export Grade</option>
            <option value="standard">Standard Grade</option>
            <option value="downgraded">Downgraded</option>
          </select>
        </CardContent>
      </Card>

      {/* Table / List View */}
      {isLoading ? (
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <Card key={i} className="h-16 animate-pulse" />
          ))}
        </div>
      ) : filtered.length === 0 ? (
        <Card className="border-dashed p-12 text-center text-muted-foreground">
          <History className="w-10 h-10 text-muted-foreground/40 mx-auto mb-2" />
          <p className="font-semibold text-sm">{t('history.noHistory')}</p>
        </Card>
      ) : (
        <Card className="overflow-hidden">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>{t('history.batchCrop')}</TableHead>
                <TableHead>{t('history.hub')}</TableHead>
                <TableHead>{t('history.harvestWeight')}</TableHead>
                <TableHead>{t('history.timesDuration')}</TableHead>
                <TableHead>Final Moisture</TableHead>
                <TableHead>{t('history.finalGrade')}</TableHead>
                <TableHead>{t('history.avoidedLoss')}</TableHead>
                <TableHead className="text-right">Details</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filtered.map((batch) => {
                const finalGrade =
                  batch.final_quality_grade || batch.predicted_quality_grade || 'standard';
                const hub = hubs.find((h) => h.id === batch.hub_id);
                const startDate = new Date(batch.start_time).toLocaleDateString([], {
                  month: 'short',
                  day: 'numeric',
                  hour: '2-digit',
                  minute: '2-digit',
                });
                const endDate = batch.end_time
                  ? new Date(batch.end_time).toLocaleDateString([], {
                      month: 'short',
                      day: 'numeric',
                      hour: '2-digit',
                      minute: '2-digit',
                    })
                  : 'N/A';
                const duration = formatBatchDuration(batch.start_time, batch.end_time);

                return (
                  <TableRow key={batch.id}>
                    <TableCell>
                      <div className="font-bold text-foreground">
                        {t(`crops.${batch.crop_type.toLowerCase()}`) || batch.crop_type}
                      </div>
                      <div className="text-[11px] font-mono text-muted-foreground">
                        #{batch.id.slice(0, 8)}
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge variant="secondary" className="text-brand-700 bg-brand-50 flex items-center w-fit">
                        <Building2 className="w-3 h-3 mr-1" />
                        {hub?.name || 'Regional Hub'}
                      </Badge>
                    </TableCell>
                    <TableCell className="font-semibold text-foreground">
                      {batch.initial_weight_kg} kg
                    </TableCell>
                    <TableCell>
                      <div className="text-xs text-foreground font-medium flex items-center">
                        <Clock className="w-3 h-3 mr-1 text-muted-foreground" />
                        {duration}
                      </div>
                      <div className="text-[11px] text-muted-foreground">
                        {startDate} → {endDate}
                      </div>
                    </TableCell>
                    <TableCell>
                      <span className="font-bold text-blue-600">
                        {batch.current_moisture_pct !== undefined
                          ? `${batch.current_moisture_pct}%`
                          : `${batch.target_moisture_pct}%`}
                      </span>
                      <span className="text-[11px] text-muted-foreground block">
                        {t('history.target', { target: batch.target_moisture_pct })}
                      </span>
                    </TableCell>
                    <TableCell>
                      <PredictionBadge grade={finalGrade} size="sm" />
                    </TableCell>
                    <TableCell>
                      {batch.avoided_loss_kg !== undefined && batch.avoided_loss_kg !== null ? (
                        <div>
                          <span className="font-semibold text-emerald-700">+{batch.avoided_loss_kg} kg</span>
                          <span className="text-[11px] text-muted-foreground block">
                            {batch.avoided_loss_kes?.toLocaleString()} KES
                          </span>
                        </div>
                      ) : (
                        <span className="text-muted-foreground text-xs">—</span>
                      )}
                    </TableCell>
                    <TableCell className="text-right">
                      <Button
                        asChild
                        variant="secondary"
                        size="sm"
                        className="text-brand-700 bg-brand-50 hover:bg-brand-100"
                      >
                        <Link to={`/batches/${batch.id}`}>
                          View
                          <ArrowRight className="w-3 h-3 ml-1" />
                        </Link>
                      </Button>
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </Card>
      )}
    </div>
  );
};
