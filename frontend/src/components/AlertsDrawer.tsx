import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import { api } from '../api/client';
import { Alert } from '../types';
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from '@/components/ui/sheet';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Bell,
  CheckCircle,
  AlertTriangle,
  Clock,
  ArrowRight,
} from 'lucide-react';

interface AlertsDrawerProps {
  isAdmin?: boolean;
}

export const AlertsDrawer: React.FC<AlertsDrawerProps> = () => {
  const { t } = useTranslation();
  const queryClient = useQueryClient();
  const [open, setOpen] = useState(false);

  // Poll unread count every 30 seconds
  const { data: unreadData } = useQuery({
    queryKey: ['alerts', 'unread-count'],
    queryFn: () => api.getUnreadAlertsCount(),
    refetchInterval: 30000,
  });
  const unreadCount = unreadData?.unread_count || 0;

  // Poll recent alerts (up to 15)
  const { data: alerts = [], isLoading } = useQuery({
    queryKey: ['alerts', 'recent'],
    queryFn: () => api.getAlerts({ limit: 15 }),
    refetchInterval: 30000,
    enabled: open,
  });

  // Mark alert as read mutation
  const markReadMutation = useMutation({
    mutationFn: (alertId: string) => api.markAlertAsRead(alertId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alerts'] });
    },
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
    <Sheet open={open} onOpenChange={setOpen}>
      <SheetTrigger asChild>
        <button
          type="button"
          data-testid="alerts-bell-trigger"
          className="relative p-2 rounded-lg text-gray-500 hover:text-gray-900 hover:bg-gray-100 transition-colors focus:outline-none focus:ring-2 focus:ring-brand-500"
          aria-label="Open notifications"
        >
          <Bell className="w-5 h-5" />
          {unreadCount > 0 && (
            <span
              data-testid="alerts-badge-count"
              className="absolute top-1 right-1 flex items-center justify-center min-w-4 h-4 px-1 text-[10px] font-bold text-white bg-red-600 rounded-full animate-pulse"
            >
              {unreadCount > 99 ? '99+' : unreadCount}
            </span>
          )}
        </button>
      </SheetTrigger>

      <SheetContent side="right" className="w-full sm:max-w-md flex flex-col p-0">
        <SheetHeader className="p-5 border-b border-border">
          <div className="flex items-center justify-between">
            <SheetTitle className="text-lg font-bold flex items-center">
              <Bell className="w-5 h-5 mr-2 text-brand-600" />
              {t('alerts.recentAlerts')}
            </SheetTitle>
            {unreadCount > 0 && (
              <Badge variant="secondary" className="bg-red-50 text-red-700 font-semibold">
                {t('alerts.unreadCount', { count: unreadCount })}
              </Badge>
            )}
          </div>
        </SheetHeader>

        <div className="flex-1 overflow-y-auto p-4 space-y-3">
          {isLoading ? (
            <div className="flex justify-center items-center py-12">
              <div className="h-6 w-6 animate-spin rounded-full border-2 border-brand-600 border-r-transparent"></div>
            </div>
          ) : alerts.length === 0 ? (
            <div className="text-center py-12 text-sm text-muted-foreground">
              {t('alerts.noAlerts')}
            </div>
          ) : (
            alerts.map((alert: Alert) => {
              const formattedTime = new Date(alert.sent_at).toLocaleTimeString([], {
                hour: '2-digit',
                minute: '2-digit',
                month: 'short',
                day: 'numeric',
              });

              return (
                <div
                  key={alert.id}
                  className={`p-3.5 rounded-xl border transition-colors ${
                    alert.is_read
                      ? 'bg-muted/30 border-border text-muted-foreground'
                      : 'bg-card border-brand-200 shadow-xs'
                  }`}
                >
                  <div className="flex items-start justify-between gap-2 mb-1.5">
                    {getAlertBadge(alert.alert_type)}
                    <span className="text-[11px] text-muted-foreground whitespace-nowrap">
                      {formattedTime}
                    </span>
                  </div>

                  <p className="text-xs font-medium text-foreground leading-relaxed">
                    {alert.message}
                  </p>

                  <div className="mt-2.5 pt-2 border-t border-border/60 flex items-center justify-between text-[11px]">
                    <span className="text-muted-foreground font-mono">
                      SMS: {alert.phone_number}
                    </span>

                    {!alert.is_read ? (
                      <Button
                        variant="ghost"
                        size="sm"
                        className="h-6 text-[11px] text-brand-700 hover:text-brand-800 hover:bg-brand-50 px-2"
                        onClick={() => markReadMutation.mutate(alert.id)}
                        disabled={markReadMutation.isPending}
                      >
                        <CheckCircle className="w-3 h-3 mr-1" />
                        {t('alerts.markRead')}
                      </Button>
                    ) : (
                      <span className="text-muted-foreground italic">{t('alerts.read')}</span>
                    )}
                  </div>
                </div>
              );
            })
          )}
        </div>

        <div className="p-4 border-t border-border bg-muted/20">
          <Button
            asChild
            variant="outline"
            className="w-full text-brand-700 border-brand-200 hover:bg-brand-50 font-semibold"
            onClick={() => setOpen(false)}
          >
            <Link to="/alerts">
              {t('alerts.viewAll')}
              <ArrowRight className="w-4 h-4 ml-1.5" />
            </Link>
          </Button>
        </div>
      </SheetContent>
    </Sheet>
  );
};
