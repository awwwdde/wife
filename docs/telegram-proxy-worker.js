// Cloudflare Worker — реверс-прокси Telegram Bot API.
// Нужен, когда у хостинга (панели) нет прямого исходящего доступа к api.telegram.org.
// Cloudflare сам достаёт до Telegram, а URL воркера доступен из панели.
//
// Как развернуть (бесплатно, без сервера):
//  1. dash.cloudflare.com → Workers & Pages → Create → Create Worker.
//  2. Вставить этот код, Deploy. Получишь URL вида https://<имя>.<акк>.workers.dev
//  3. В панели askbrows задать переменную:
//        TELEGRAM_API_BASE=https://<имя>.<акк>.workers.dev
//     затем Rebuild под-сайта.
//
// Проверка воркера в браузере (замени <TOKEN>):
//   https://<имя>.<акк>.workers.dev/bot<TOKEN>/getMe  → должен вернуть JSON {"ok":true,...}
//
// Примечание: воркер проксирует только на api.telegram.org. Токен идёт в пути (как и
// при прямом обращении к Bot API) — это нормально; храни URL/токен как секрет.

export default {
  async fetch(request) {
    const url = new URL(request.url);
    url.hostname = "api.telegram.org";
    url.protocol = "https:";
    url.port = "";
    return fetch(new Request(url.toString(), request));
  },
};
