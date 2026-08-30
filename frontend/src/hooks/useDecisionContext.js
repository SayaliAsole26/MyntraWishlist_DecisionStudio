import { useCallback, useState } from "react";
import {
  compareOptionsFromContext,
  getDecisionContext,
  saveDecisionContext,
} from "../lib/decisionContext.js";

export function useDecisionContext() {
  const [context, setContextState] = useState(() => getDecisionContext());

  const setContext = useCallback((partial) => {
    const next = saveDecisionContext(partial);
    setContextState(next);
    return next;
  }, []);

  const compareOptions = useCallback(
    () => compareOptionsFromContext(context),
    [context]
  );

  return { context, setContext, compareOptions };
}
