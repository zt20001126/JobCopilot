export interface PageWatcherOptions {
  onPageChange: () => void;
  debounceMs?: number;
}

export interface PageWatcher {
  stop: () => void;
}

/**
 * 监听单页应用的路由和 DOM 变化，并通过防抖合并高频更新。
 */
export function watchPageChanges({
  onPageChange,
  debounceMs = 250,
}: PageWatcherOptions): PageWatcher {
  let timerId: number | undefined;
  const originalPushState = history.pushState;
  const originalReplaceState = history.replaceState;

  const scheduleChange = () => {
    window.clearTimeout(timerId);
    timerId = window.setTimeout(onPageChange, debounceMs);
  };

  history.pushState = function (...args) {
    originalPushState.apply(this, args);
    scheduleChange();
  };

  history.replaceState = function (...args) {
    originalReplaceState.apply(this, args);
    scheduleChange();
  };

  window.addEventListener("popstate", scheduleChange);

  const observer = new MutationObserver(scheduleChange);
  observer.observe(document.documentElement, {
    childList: true,
    subtree: true,
  });

  return {
    stop() {
      window.clearTimeout(timerId);
      observer.disconnect();
      window.removeEventListener("popstate", scheduleChange);
      history.pushState = originalPushState;
      history.replaceState = originalReplaceState;
    },
  };
}
