/* Evolute Training - service worker (avisos do sistema, som e número no ícone). Não guarda nada em cache. */
self.addEventListener("install", function () { self.skipWaiting(); });
self.addEventListener("activate", function (e) { e.waitUntil(self.clients.claim()); });
self.addEventListener("push", function (e) {
  var d = {};
  try { d = e.data ? e.data.json() : {}; } catch (x) { d = { body: e.data ? e.data.text() : "" }; }
  var title = d.title || "Evolute Training";
  var opts = { body: d.body || "", tag: d.tag || "evolute", renotify: true, silent: false, vibrate: [200, 100, 200, 100, 200],
    icon: "praticantes-icon-192.png", badge: "praticantes-icon-192.png", data: { url: d.url || "./" } };
  e.waitUntil(self.clients.matchAll({ type: "window", includeUncontrolled: true }).then(function (list) {
    var jobs = [];
    var visible = list.some(function (c) { return c.visibilityState === "visible"; });
    if (!visible) jobs.push(self.registration.showNotification(title, opts)); /* com o app aberto, o próprio app avisa */
    try { if (d.n != null && self.navigator && self.navigator.setAppBadge) jobs.push(d.n > 0 ? self.navigator.setAppBadge(d.n) : self.navigator.clearAppBadge()); } catch (x) {}
    return Promise.all(jobs.map(function (p) { return Promise.resolve(p).catch(function () {}); }));
  }));
});
self.addEventListener("notificationclick", function (e) {
  e.notification.close();
  var url = (e.notification.data && e.notification.data.url) || "./";
  e.waitUntil(self.clients.matchAll({ type: "window", includeUncontrolled: true }).then(function (list) {
    for (var i = 0; i < list.length; i++) { if ("focus" in list[i]) return list[i].focus(); }
    return self.clients.openWindow(url);
  }));
});

/* Atualização: a página principal é sempre buscada na rede, sem cache do navegador (o app instalado ficava com a versão velha). */
self.addEventListener("fetch", function (e) {
  var r = e.request;
  if (r.mode !== "navigate") return;
  e.respondWith(fetch(r.url, { cache: "no-store", credentials: "same-origin" }).catch(function () { return fetch(r); }));
});
