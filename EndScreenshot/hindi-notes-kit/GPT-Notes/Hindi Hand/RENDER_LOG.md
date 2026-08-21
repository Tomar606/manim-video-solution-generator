# Render log — Hindi Hand PYQ pages

One row per **billed** image call (retries included, because a retry is a second
charge). The `page` id carries its own board+chapter, so all chapters share one log.
Token columns are what the API reported; `est $` prices them with PRICE_TEXT_IN /
PRICE_IMAGE_IN / PRICE_IMAGE_OUT (per 1M tokens), so it is only as right as those.

| UTC | page | attempt | result | model | quality | size | prompt | refs | txt-in | img-in | out | est $ |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026-08-16 16:25 | mp-ch1-page-01 | 1 | saved | gpt-image-2 | medium | 1024x1536 | 21804 ch | 3 | 5444 | 2144 | 1372 | 0.104 |
| 2026-08-16 16:29 | mp-ch1-page-01 | 1 | saved | gpt-image-2 | medium | 1024x1536 | 21634 ch | 3 | 5377 | 2144 | 1372 | 0.103 |
| 2026-08-16 16:36 | mp-ch1-page-01 | 1 | saved | gpt-image-2 | medium | 1024x1536 | 22297 ch | 3 | 5524 | 2144 | 1372 | 0.104 |
| 2026-08-16 16:39 | mp-ch1-dia-01 | 1 | saved | gpt-image-2 | medium | 1024x1536 | 8325 ch | 3 | 2047 | 2560 | 1372 | 0.091 |
| 2026-08-16 16:40 | mp-ch1-page-02 | 1 | saved | gpt-image-2 | medium | 1024x1536 | 21941 ch | 3 | 5414 | 2144 | 1372 | 0.103 |
| 2026-08-16 16:41 | mp-ch1-page-03 | 1 | saved | gpt-image-2 | medium | 1024x1536 | 21918 ch | 3 | 5417 | 2144 | 1372 | 0.103 |
| 2026-08-16 16:42 | mp-ch1-page-04 | 1 | saved | gpt-image-2 | medium | 1024x1536 | 21876 ch | 3 | 5372 | 2144 | 1372 | 0.103 |
| 2026-08-16 16:43 | mp-ch1-page-05 | 1 | saved | gpt-image-2 | medium | 1024x1536 | 21494 ch | 3 | 5288 | 2144 | 1372 | 0.103 |
| 2026-08-16 16:44 | mp-ch2-dia-01 | 1 | saved | gpt-image-2 | medium | 1024x1536 | 8325 ch | 3 | 2046 | 2496 | 1372 | 0.090 |
| 2026-08-16 16:44 | mp-ch2-dia-03 | 1 | saved | gpt-image-2 | medium | 1024x1536 | 8322 ch | 3 | 2045 | 2656 | 1372 | 0.092 |
| 2026-08-16 16:45 | mp-ch2-dia-04 | 1 | saved | gpt-image-2 | medium | 1024x1536 | 8319 ch | 3 | 2043 | 2528 | 1372 | 0.090 |
| 2026-08-16 16:46 | mp-ch2-page-01 | 1 | saved | gpt-image-2 | medium | 1024x1536 | 22046 ch | 3 | 5428 | 2144 | 1372 | 0.103 |
| 2026-08-16 16:47 | mp-ch2-page-02 | 1 | saved | gpt-image-2 | medium | 1024x1536 | 22024 ch | 3 | 5435 | 2144 | 1372 | 0.103 |
| 2026-08-16 16:48 | mp-ch2-page-03 | 1 | saved | gpt-image-2 | medium | 1024x1536 | 21947 ch | 3 | 5398 | 2144 | 1372 | 0.103 |
| 2026-08-16 16:49 | mp-ch2-page-04 | 1 | saved | gpt-image-2 | medium | 1024x1536 | 21778 ch | 3 | 5360 | 2144 | 1372 | 0.103 |
| 2026-08-16 16:50 | mp-ch2-page-05 | 1 | saved | gpt-image-2 | medium | 1024x1536 | 21946 ch | 3 | 5391 | 2144 | 1372 | 0.103 |
| 2026-08-16 16:51 | mp-ch2-page-06 | 1 | saved | gpt-image-2 | medium | 1024x1536 | 21856 ch | 3 | 5340 | 2144 | 1372 | 0.103 |
| 2026-08-16 16:52 | mp-ch2-page-07 | 1 | saved | gpt-image-2 | medium | 1024x1536 | 21454 ch | 3 | 5222 | 2144 | 1372 | 0.102 |
| 2026-08-16 16:52 | mp-ch6-dia-01 | 1 | saved | gpt-image-2 | medium | 1024x1536 | 8544 ch | 3 | 2122 | 2720 | 1372 | 0.093 |
| 2026-08-16 16:54 | mp-ch6-page-01 | 1 | saved | gpt-image-2 | medium | 1024x1536 | 21875 ch | 3 | 5366 | 2144 | 1372 | 0.103 |
| 2026-08-16 16:54 | mp-ch6-page-02 | 1 | saved | gpt-image-2 | medium | 1024x1536 | 21930 ch | 3 | 5342 | 2144 | 1372 | 0.103 |
| 2026-08-16 16:55 | mp-ch6-page-03 | 1 | saved | gpt-image-2 | medium | 1024x1536 | 21951 ch | 3 | 5369 | 2144 | 1372 | 0.103 |
| 2026-08-16 16:56 | mp-ch6-page-04 | 1 | saved | gpt-image-2 | medium | 1024x1536 | 22047 ch | 3 | 5407 | 2144 | 1372 | 0.103 |
| 2026-08-16 16:57 | mp-ch6-page-05 | 1 | saved | gpt-image-2 | medium | 1024x1536 | 21899 ch | 3 | 5385 | 2144 | 1372 | 0.103 |
| 2026-08-16 16:58 | mp-ch6-page-06 | 1 | saved | gpt-image-2 | medium | 1024x1536 | 20954 ch | 3 | 5028 | 2144 | 1372 | 0.101 |
| 2026-08-16 16:59 | mp-ch7-page-01 | 1 | saved | gpt-image-2 | medium | 1024x1536 | 21904 ch | 3 | 5379 | 2144 | 1372 | 0.103 |
| 2026-08-16 17:01 | mp-ch7-page-02 | 1 | saved | gpt-image-2 | medium | 1024x1536 | 21846 ch | 3 | 5354 | 2144 | 1372 | 0.103 |
| 2026-08-16 17:02 | mp-ch7-page-03 | 1 | saved | gpt-image-2 | medium | 1024x1536 | 21971 ch | 3 | 5395 | 2144 | 1372 | 0.103 |
| 2026-08-16 17:02 | mp-ch7-page-04 | 1 | saved | gpt-image-2 | medium | 1024x1536 | 21754 ch | 3 | 5360 | 2144 | 1372 | 0.103 |
| 2026-08-16 17:03 | mp-ch7-page-05 | 1 | saved | gpt-image-2 | medium | 1024x1536 | 21628 ch | 3 | 5309 | 2144 | 1372 | 0.103 |
| 2026-08-16 17:04 | mp-ch7-page-06 | 1 | saved | gpt-image-2 | medium | 1024x1536 | 21814 ch | 3 | 5303 | 2144 | 1372 | 0.103 |
| 2026-08-16 17:05 | mp-ch7-page-07 | 1 | saved | gpt-image-2 | medium | 1024x1536 | 22404 ch | 3 | 5538 | 2144 | 1372 | 0.104 |
| 2026-08-16 17:06 | rj-ch1-dia-01 | 1 | saved | gpt-image-2 | medium | 1024x1536 | 8335 ch | 3 | 2054 | 2720 | 1372 | 0.092 |
| 2026-08-16 17:07 | rj-ch1-dia-02 | 1 | saved | gpt-image-2 | medium | 1024x1536 | 8343 ch | 3 | 2062 | 2496 | 1372 | 0.090 |
| 2026-08-16 17:08 | rj-ch1-page-01 | 1 | saved | gpt-image-2 | medium | 1024x1536 | 21945 ch | 3 | 5442 | 2144 | 1372 | 0.104 |
| 2026-08-16 17:09 | rj-ch1-page-02 | 1 | saved | gpt-image-2 | medium | 1024x1536 | 21967 ch | 3 | 5409 | 2144 | 1372 | 0.103 |
| 2026-08-16 17:10 | rj-ch1-page-03 | 1 | saved | gpt-image-2 | medium | 1024x1536 | 22364 ch | 3 | 5585 | 2144 | 1372 | 0.104 |
| 2026-08-16 17:11 | rj-ch1-page-04 | 1 | saved | gpt-image-2 | medium | 1024x1536 | 21901 ch | 3 | 5421 | 2144 | 1372 | 0.103 |
| 2026-08-16 17:12 | rj-ch1-page-05 | 1 | saved | gpt-image-2 | medium | 1024x1536 | 21952 ch | 3 | 5434 | 2144 | 1372 | 0.103 |
| 2026-08-16 17:13 | rj-ch1-page-06 | 1 | saved | gpt-image-2 | medium | 1024x1536 | 22121 ch | 3 | 5473 | 2144 | 1372 | 0.104 |
| 2026-08-16 17:14 | rj-ch1-page-07 | 1 | saved | gpt-image-2 | medium | 1024x1536 | 21765 ch | 3 | 5328 | 2144 | 1372 | 0.103 |
| 2026-08-16 17:14 | rj-ch2-dia-01 | 1 | saved | gpt-image-2 | medium | 1024x1536 | 8319 ch | 3 | 2047 | 2656 | 1372 | 0.092 |
| 2026-08-16 17:15 | rj-ch2-page-01 | 1 | saved | gpt-image-2 | medium | 1024x1536 | 21926 ch | 3 | 5411 | 2144 | 1372 | 0.103 |
| 2026-08-16 17:16 | rj-ch2-page-02 | 1 | saved | gpt-image-2 | medium | 1024x1536 | 21948 ch | 3 | 5393 | 2144 | 1372 | 0.103 |
| 2026-08-16 17:17 | rj-ch2-page-03 | 1 | saved | gpt-image-2 | medium | 1024x1536 | 21918 ch | 3 | 5385 | 2144 | 1372 | 0.103 |
| 2026-08-16 17:18 | rj-ch2-page-04 | 1 | saved | gpt-image-2 | medium | 1024x1536 | 21496 ch | 3 | 5247 | 2144 | 1372 | 0.103 |
| 2026-08-16 17:19 | rj-ch2-page-05 | 1 | saved | gpt-image-2 | medium | 1024x1536 | 22005 ch | 3 | 5425 | 2144 | 1372 | 0.103 |
| 2026-08-16 17:20 | rj-ch2-page-06 | 1 | saved | gpt-image-2 | medium | 1024x1536 | 21741 ch | 3 | 5323 | 2144 | 1372 | 0.103 |
| 2026-08-16 17:21 | rj-ch2-page-07 | 1 | saved | gpt-image-2 | medium | 1024x1536 | 22234 ch | 3 | 5485 | 2144 | 1372 | 0.104 |
| 2026-08-16 17:21 | rj-ch2-page-08 | 1 | saved | gpt-image-2 | medium | 1024x1536 | 21857 ch | 3 | 5357 | 2144 | 1372 | 0.103 |
| 2026-08-16 17:22 | rj-ch2-page-09 | 1 | saved | gpt-image-2 | medium | 1024x1536 | 21325 ch | 3 | 5179 | 2144 | 1372 | 0.102 |
| 2026-08-16 17:23 | rj-ch6-page-01 | 1 | saved | gpt-image-2 | medium | 1024x1536 | 21874 ch | 3 | 5390 | 2144 | 1372 | 0.103 |
| 2026-08-16 17:24 | rj-ch6-page-02 | 1 | saved | gpt-image-2 | medium | 1024x1536 | 21934 ch | 3 | 5359 | 2144 | 1372 | 0.103 |
| 2026-08-16 17:25 | rj-ch6-page-03 | 1 | saved | gpt-image-2 | medium | 1024x1536 | 22017 ch | 3 | 5390 | 2144 | 1372 | 0.103 |
| 2026-08-16 17:26 | rj-ch6-page-04 | 1 | saved | gpt-image-2 | medium | 1024x1536 | 21955 ch | 3 | 5382 | 2144 | 1372 | 0.103 |
| 2026-08-16 17:27 | rj-ch6-page-05 | 1 | saved | gpt-image-2 | medium | 1024x1536 | 21839 ch | 3 | 5308 | 2144 | 1372 | 0.103 |
| 2026-08-16 17:28 | rj-ch6-page-06 | 1 | saved | gpt-image-2 | medium | 1024x1536 | 21880 ch | 3 | 5324 | 2144 | 1372 | 0.103 |
| 2026-08-16 17:29 | rj-ch6-page-07 | 1 | saved | gpt-image-2 | medium | 1024x1536 | 21713 ch | 3 | 5299 | 2144 | 1372 | 0.103 |
| 2026-08-16 17:30 | rj-ch7-page-01 | 1 | saved | gpt-image-2 | medium | 1024x1536 | 21696 ch | 3 | 5285 | 2144 | 1372 | 0.103 |
| 2026-08-16 17:31 | rj-ch7-page-02 | 1 | saved | gpt-image-2 | medium | 1024x1536 | 22115 ch | 3 | 5431 | 2144 | 1372 | 0.103 |
| 2026-08-16 17:32 | rj-ch7-page-03 | 1 | saved | gpt-image-2 | medium | 1024x1536 | 21940 ch | 3 | 5402 | 2144 | 1372 | 0.103 |
| 2026-08-16 17:33 | rj-ch7-page-04 | 1 | saved | gpt-image-2 | medium | 1024x1536 | 21817 ch | 3 | 5345 | 2144 | 1372 | 0.103 |
| 2026-08-16 17:33 | rj-ch7-page-05 | 1 | saved | gpt-image-2 | medium | 1024x1536 | 21957 ch | 3 | 5366 | 2144 | 1372 | 0.103 |
| 2026-08-16 17:34 | rj-ch7-page-06 | 1 | saved | gpt-image-2 | medium | 1024x1536 | 21787 ch | 3 | 5309 | 2144 | 1372 | 0.103 |
| 2026-08-16 17:35 | rj-ch7-page-07 | 1 | saved | gpt-image-2 | medium | 1024x1536 | 22095 ch | 3 | 5405 | 2144 | 1372 | 0.103 |
| 2026-08-16 17:36 | rj-ch7-page-08 | 1 | saved | gpt-image-2 | medium | 1024x1536 | 21076 ch | 3 | 5097 | 2144 | 1372 | 0.102 |
| 2026-08-17 11:31 | up-ch1-page-01 | 1 | saved | gpt-image-2 | medium | 1024x1536 | 21971 ch | 3 | 5406 | 2144 | 1372 | 0.103 |
| 2026-08-17 11:32 | up-ch1-page-02 | 1 | saved | gpt-image-2 | medium | 1024x1536 | 21888 ch | 3 | 5374 | 2144 | 1372 | 0.103 |
