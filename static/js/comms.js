export function postMessage(message) {
    window.parent.postMessage(message, '*');
}
