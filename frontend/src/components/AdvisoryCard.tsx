import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Sparkles, MessageSquare } from 'lucide-react';

interface AdvisoryCardProps {
  advisoryEn?: string;
  advisorySw?: string;
}

export const AdvisoryCard: React.FC<AdvisoryCardProps> = ({
  advisoryEn,
  advisorySw,
}) => {
  const { t, i18n } = useTranslation();
  const isSw = i18n.language === 'sw';
  const [showBilingual, setShowBilingual] = useState(false);

  const primaryMessage = isSw
    ? advisorySw || advisoryEn || 'Inakusanya vipimo...'
    : advisoryEn || advisorySw || 'Collecting initial readings...';

  const secondaryMessage = isSw ? advisoryEn : advisorySw;

  return (
    <div className="rounded-xl border border-amber-200 bg-gradient-to-r from-amber-50 to-orange-50 p-4 shadow-sm">
      <div className="flex items-start space-x-3">
        <div className="w-8 h-8 rounded-lg bg-solar-500/10 text-solar-600 flex items-center justify-center flex-shrink-0 mt-0.5">
          <Sparkles className="w-5 h-5 text-solar-600" />
        </div>
        <div className="flex-1">
          <div className="flex items-center justify-between">
            <h4 className="text-xs font-bold uppercase tracking-wider text-solar-800 flex items-center">
              <MessageSquare className="w-3.5 h-3.5 mr-1" />
              {t('detail.advisoryTitle')}
            </h4>
            {secondaryMessage && (
              <button
                type="button"
                onClick={() => setShowBilingual(!showBilingual)}
                className="text-[11px] font-semibold text-solar-700 hover:text-solar-900 underline"
              >
                {showBilingual ? 'Hide alternate' : 'Show EN/SW'}
              </button>
            )}
          </div>
          <p className="mt-1 text-sm font-semibold text-gray-900 leading-snug">
            {primaryMessage}
          </p>
          {showBilingual && secondaryMessage && (
            <p className="mt-2 text-xs italic text-gray-600 border-t border-amber-200/60 pt-1.5">
              <span className="font-semibold">{isSw ? 'English:' : 'Kiswahili:'}</span> {secondaryMessage}
            </p>
          )}
        </div>
      </div>
    </div>
  );
};
