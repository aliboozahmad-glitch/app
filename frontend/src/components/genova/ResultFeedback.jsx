import { useEffect, useState } from "react";
import PropTypes from "prop-types";
import { ThumbsDown, ThumbsUp } from "lucide-react";
import { toast } from "sonner";
import { useLang } from "@/i18n/LanguageContext";
import { useApi, errorMessage } from "@/lib/api";

const pill = (on) =>
  `inline-flex items-center gap-2 text-sm px-3 py-1.5 rounded-md border transition-colors ${on ? "bg-slate-900 text-white border-slate-900" : "border-slate-300 hover:border-slate-500"}`;

const Rating = ({ value, onRate }) => {
  const { t } = useLang();
  return (
    <div className="flex items-center gap-3 flex-wrap" data-testid="result-rating">
      <span className="text-sm text-slate-600">{t.feedback.helpful}</span>
      <button type="button" className={pill(value === "like")} onClick={() => onRate("like")} aria-pressed={value === "like"} data-testid="rating-like-button">
        <ThumbsUp size={15} /> {t.feedback.like}
      </button>
      <button type="button" className={pill(value === "dislike")} onClick={() => onRate("dislike")} aria-pressed={value === "dislike"} data-testid="rating-dislike-button">
        <ThumbsDown size={15} /> {t.feedback.dislike}
      </button>
    </div>
  );
};

Rating.propTypes = { value: PropTypes.oneOf(["like", "dislike", null]), onRate: PropTypes.func.isRequired };

const StageRow = ({ stage, saved, onConfirm }) => {
  const { t } = useLang();
  const actual = saved?.actual;
  return (
    <div className="flex items-center gap-3 flex-wrap" data-testid={`confirm-${stage}`}>
      <span className="text-sm w-40 text-slate-700">{t.feedback.stages[stage]}</span>
      {["male", "female"].map((g) => (
        <button key={g} type="button" className={pill(actual === g)} aria-pressed={actual === g} onClick={() => onConfirm(stage, g)}
          data-testid={`confirm-${stage}-${g}`}>
          {g === "male" ? t.family.boy : t.family.girl}
        </button>
      ))}
      {actual && <span className="text-xs text-emerald-700" data-testid={`confirm-${stage}-saved`}>{t.feedback.saved}</span>}
    </div>
  );
};

StageRow.propTypes = {
  stage: PropTypes.oneOf(["pregnancy", "birth"]).isRequired,
  saved: PropTypes.shape({ actual: PropTypes.string }),
  onConfirm: PropTypes.func.isRequired,
};

const Confirmations = ({ saved, onConfirm }) => {
  const { t } = useLang();
  return (
    <div className="border border-slate-200 rounded-md p-4 space-y-3 bg-slate-50" data-testid="result-confirmations">
      <div>
        <h3 className="font-semibold text-sm">{t.feedback.confirmTitle}</h3>
        <p className="text-xs text-slate-600 mt-1">{t.feedback.confirmNote}</p>
      </div>
      <StageRow stage="pregnancy" saved={saved.pregnancy} onConfirm={onConfirm} />
      <StageRow stage="birth" saved={saved.birth} onConfirm={onConfirm} />
    </div>
  );
};

Confirmations.propTypes = { saved: PropTypes.object.isRequired, onConfirm: PropTypes.func.isRequired };

export const ResultFeedback = ({ analysisId }) => {
  const api = useApi();
  const { t } = useLang();
  const [fb, setFb] = useState(null);
  useEffect(() => {
    let active = true;
    api("get", `/analyses/${analysisId}/feedback`).then((d) => active && setFb(d)).catch(() => active && setFb(null));
    return () => { active = false; };
  }, [api, analysisId]);
  if (!fb) return null;
  const save = async (path, body, apply) => {
    try {
      await api("put", `/analyses/${analysisId}/${path}`, body);
      setFb((f) => apply(f));
      toast.success(t.feedback.thanks);
    } catch (e) {
      toast.error(errorMessage(e, t.c.error));
    }
  };
  const onRate = (value) => save("rating", { value }, (f) => ({ ...f, rating: value }));
  const onConfirm = (stage, actual) => save(`confirmations/${stage}`, { actual },
    (f) => ({ ...f, confirmations: { ...f.confirmations, [stage]: { actual } } }));
  return (
    <div className="no-print space-y-4 pt-2" data-testid="result-feedback">
      <Rating value={fb.rating} onRate={onRate} />
      {fb.confirmable && <Confirmations saved={fb.confirmations} onConfirm={onConfirm} />}
    </div>
  );
};

ResultFeedback.propTypes = { analysisId: PropTypes.string.isRequired };
