import { useEffect, useState } from 'react';

interface UseCountUpOptions {
  duration?: number;
  start?: number;
  end: number;
  decimals?: number;
  enabled?: boolean;
}

export function useCountUp({
  duration = 2000,
  start = 0,
  end,
  decimals = 0,
  enabled = true,
}: UseCountUpOptions) {
  const [count, setCount] = useState(start);

  useEffect(() => {
    if (!enabled) {
      setCount(end);
      return;
    }

    const startTime = Date.now();
    const difference = end - start;

    const updateCount = () => {
      const elapsed = Date.now() - startTime;
      const progress = Math.min(elapsed / duration, 1);

      // Easing function (ease-out)
      const easeOut = 1 - Math.pow(1 - progress, 3);
      const current = start + difference * easeOut;

      setCount(Number(current.toFixed(decimals)));

      if (progress < 1) {
        requestAnimationFrame(updateCount);
      } else {
        setCount(end);
      }
    };

    const frameId = requestAnimationFrame(updateCount);
    return () => cancelAnimationFrame(frameId);
  }, [start, end, duration, decimals, enabled]);

  return count;
}
