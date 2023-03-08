class Timer {
  constructor(prefix, timeit) {
    this.prefix = prefix;
    this.timeit = timeit;
    this.start = performance.now();
    if (timeit) {
      console.info(`three-cad-viewer: Timer ${prefix}:start`);
    }
  }

  split(msg) {
    if (this.timeit) {
      const t = performance.now();
      console.info(
        `three-cad-viewer: Timer ${this.prefix}:${msg} ${(
          t - this.start
        ).toFixed(1)} ms`,
      );
    }
  }

  stop() {
    if (this.timeit) {
      const t = performance.now();
      console.info(
        `three-cad-viewer: Timer ${this.prefix}:stop ${(t - this.start).toFixed(
          1,
        )} ms`,
      );
    }
  }
}

export { Timer };
