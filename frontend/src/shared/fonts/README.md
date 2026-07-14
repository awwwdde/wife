# Шрифты (self-host)

Решение (DECISIONS §4): шрифты **self-host**, без запросов к Google Fonts.

Положи сюда `.woff2` и раскомментируй `@font-face` в [`fonts.css`](fonts.css):

- **Заголовки (serif):** Cormorant или Playfair Display
- **Текст (sans):** Inter или Manrope
- **Рукописный акцент:** на 1–2 элемента (приветствие)

Пока файлов нет — работают системные фолбэки, сборка не падает.
