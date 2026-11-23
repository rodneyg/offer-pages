function trackStripeCheckout(event) {
  const anchor = event.target.closest('a[href^="https://buy.stripe.com/"]');
  if (!anchor) return;

  const reference = new URL(anchor.href).searchParams.get('client_reference_id');
  if (!reference) return;

  if (!navigator.sendBeacon('/api/checkout-click', reference)) {
    fetch('/api/checkout-click', {
      method: 'POST',
      body: reference,
      keepalive: true,
    }).catch(() => {});
  }
}

document.addEventListener('click', trackStripeCheckout);
document.addEventListener('auxclick', (event) => {
  if (event.button === 1) trackStripeCheckout(event);
});
