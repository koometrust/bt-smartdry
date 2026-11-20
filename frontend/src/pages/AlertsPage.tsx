import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import { api } from '../api/client';
import { useAuth } from '../context/AuthContext';
import { Alert } from '../types';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  Bell,
  CheckCircle,
  AlertTriangle,
  Clock,
  Filter,
  Phone,
} from 'lucide-react';

export const AlertsPage: React.FC = () => {
  const { t } = useTranslation();
  const { isAdmin } = useAuth();
  const queryClient = useQueryClient();

  const [selectedHub, setSelectedHub] = useState<string>('all');
  const [selectedType, setSelectedType] = useState<string>('all');
  const [selectedStatus, setSelectedStatus] = useState<string>('all');

  const { data: hubs = [] } = useQuery({
    queryKey: ['hubs'],
    queryFn: () => api.getHubs(),
  });

  const { data: alerts = [], isLoading } = useQuery({
    queryKey: ['alerts', 'list', selectedHub, selectedType],
    queryFn: () =>
      api.getAlerts({
        hub_id: selectedHub !== 'all' ? selectedHub : undefined,
        alert_type: selectedType !== 'all' ? selectedType : undefined,
        limit: 100,
      }),
    refetchInterval: 30000,
  });

  const markReadMutation = useMutation({
    mutationFn: (alertId: string) => api.markAlertAsRead(alertId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alerts'] });
    },
  });

  const filteredAlerts = alerts.filter((alert: Alert) => {
    if (selectedStatus === 'unread' && alert.is_read) return false;
    if (selectedStatus === 'read' && !alert.is_read) return false;
    return true;
  });

  const getAlertBadge = (type: string) => {
    const tLower = type.toLowerCase();
    if (tLower.includes('near')) {
      return (
        <Badge variant="outline" className="bg-amber-50 text-amber-800 border-amber-300">
          <Clock className="w-3 h-3 mr-1" />
          {t('alerts.types.near_completion')}
        </Badge>
      );
    }
    if (tLower.includes('completion')) {
      return (
        <Badge variant="outline" className="bg-emerald-50 text-emerald-800 border-emerald-300">
          <CheckCircle className="w-3 h-3 mr-1" />
          {t('alerts.types.completion')}
        </Badge>
      );
    }
    return (
      <Badge variant="outline" className="bg-red-50 text-red-800 border-red-300">
        <AlertTriangle className="w-3 h-3 mr-1" />
        {t('alerts.types.anomaly')}
      </Badge>
    );
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-extrabold text-foreground tracking-tight flex items-center">
            <Bell className="w-6 h-6 mr-2.5 text-brand-600" />
            {t('alerts.title')}
          </h1>
          <p className="mt-1 text-sm text-muted-foreground">{t('alerts.subtitle')}</p>
        </div>
      </div>

      {/* Filter Toolbar */}
      <Card>
        <CardContent className="p-4">
          <div className="flex flex-wrap items-center gap-3">
            <div className="flex items-center text-xs font-bold text-muted-foreground uppercase tracking-wider mr-2">
              <Filter className="w-3.5 h-3.5 mr-1" />
              Filters:
            </div>

            {/* Hub Filter (for Admins) */}
            {isAdmin && (
              <select
                aria-label={t('alerts.filterHub')}
                value={selectedHub}
                onChange={(e) => setSelectedHub(e.target.value)}
                className="h-9 px-3 rounded-lg border border-border bg-background text-xs font-medium text-foreground focus:ring-2 focus:ring-brand-500 focus:outline-none"
              >
                <option value="all">{t('history.allHubs')}</option>
                {hubs.map((hub) => (
                  <option key={hub.id} value={hub.id}>
                    {hub.name}
                  </option>
                ))}
              </select>
            )}

            {/* Alert Type Filter */}
            <select
              aria-label={t('alerts.filterType')}
              value={selectedType}
              onChange={(e) => setSelectedType(e.target.value)}
              className="h-9 px-3 rounded-lg border border-border bg-background text-xs font-medium text-foreground focus:ring-2 focus:ring-brand-500 focus:outline-none"
            >
              <option value="all">{t('alerts.allTypes')}</option>
              <option value="near_completion">{t('alerts.types.near_completion')}</option>
              <option value="completion">{t('alerts.types.completion')}</option>
              <option value="anomaly">{t('alerts.types.anomaly')}</option>
            </select>

            {/* Read Status Filter */}
            <select
              aria-label={t('alerts.readStatus')}
              value={selectedStatus}
              onChange={(e) => setSelectedStatus(e.target.value)}
              className="h-9 px-3 rounded-lg border border-border bg-background text-xs font-medium text-foreground focus:ring-2 focus:ring-brand-500 focus:outline-none"
            >
              <option value="all">{t('alerts.readStatus')}: All</option>
              <option value="unread">{t('alerts.unread')}</option>
              <option value="read">{t('alerts.read')}</option>
            </select>
          </div>
        </CardContent>
      </Card>

      {/* Alerts Table */}
      <Card className="overflow-hidden">
        {isLoading ? (
          <div className="flex justify-center items-center py-20">
            <div className="h-8 w-8 animate-spin rounded-full border-4 border-brand-600 border-r-transparent"></div>
          </div>
        ) : filteredAlerts.length === 0 ? (
          <div className="text-center py-16 text-muted-foreground">
            <Bell className="w-8 h-8 mx-auto text-muted-foreground/50 mb-2" />
            <p className="text-sm">{t('alerts.noAlerts')}</p>
          </div>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>{t('alerts.type')}</TableHead>
                <TableHead>Batch ID</TableHead>
                <TableHead>{t('alerts.message')}</TableHead>
                <TableHead>{t('alerts.recipient')}</TableHead>
                <TableHead>{t('alerts.timestamp')}</TableHead>
                <TableHead className="text-right">Action</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredAlerts.map((alert: Alert) => {
                const formattedTime = new Date(alert.sent_at).toLocaleDateString([], {
                  month: 'short',
                  day: 'numeric',
                  hour: '2-digit',
                  minute: '2-digit',
                });

                return (
                  <TableRow
                    key={alert.id}
                    className={alert.is_read ? 'opacity-70 bg-muted/10' : 'bg-card font-medium'}
                  >
                    <TableCell>{getAlertBadge(alert.alert_type)}</TableCell>
                    <TableCell className="font-mono text-xs">
                      <Link
                        to={`/batches/${alert.batch_id}`}
                        className="text-brand-700 hover:underline"
                      >
                        #{alert.batch_id.slice(0, 8)}
                      </Link>
                    </TableCell>
                    <TableCell className="text-xs max-w-xs sm:max-w-md">{alert.message}</TableCell>
                    <TableCell>
                      <div className="text-xs font-mono flex items-center">
                        <Phone className="w-3 h-3 mr-1 text-muted-foreground" />
                        {alert.phone_number}
                      </div>
                      <span className="text-[10px] text-muted-foreground uppercase">
                        {alert.channel}
                      </span>
                    </TableCell>
                    <TableCell className="text-xs text-muted-foreground whitespace-nowrap">
                      {formattedTime}
                    </TableCell>
                    <TableCell className="text-right">
                      {!alert.is_read ? (
                        <Button
                          variant="outline"
                          size="sm"
                          className="text-xs h-7 border-brand-200 text-brand-700 hover:bg-brand-50"
                          onClick={() => markReadMutation.mutate(alert.id)}
                          disabled={markReadMutation.isPending}
                        >
                          <CheckCircle className="w-3.5 h-3.5 mr-1" />
                          {t('alerts.markRead')}
                        </Button>
                      ) : (
                        <span className="text-xs text-muted-foreground italic">
                          {t('alerts.read')}
                        </span>
                      )}
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        )}
      </Card>
    </div>
  );
};
