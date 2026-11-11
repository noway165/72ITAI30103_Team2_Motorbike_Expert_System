# Nguồn tài liệu cho luật

Mỗi luật ghi nguồn ở trường `source` trong file JSON. File này gom các nguồn lại để trích dẫn trong báo cáo. Mỗi người bổ sung phần hệ thống mình phụ trách.

## Động cơ (`engine.json`) và truyền động (`transmission.json`) — Giang

| Nguồn | Dùng cho luật |
|---|---|
| Motorcyclist, "What Causes a Motorcycle To Smoke?", https://motorcyclistonline.com/what-causes-motorcycle-to-smoke | EN01, EN02, EN03, EN14, EN17 |
| Partzilla, "Exhaust Smoke Color: What it Means", https://www.partzilla.com/blog/exhaust-smoke-colors-meaning | EN01, EN07, EN13 |
| Honda CRF250R owner's manual, "Air Cleaner", https://www.bike-parts.fr/thumbs/pdf_url/img/owner_manuals/owner_CRF250RA_EN/2500_2500/0057.pdf | EN04, EN14, EN17 |
| Honda owner's manuals, "Engine Oil" (ví dụ CRF150F), https://www.bike-parts.fr/thumbs/pdf_url/img/owner_manuals/owner_CRF150FE_EN/2500_2500/0070.pdf | EN05 |
| Ultimate Motorcycling, "Top 6 Strange Motorcycle Noises", https://ultimatemotorcycling.com/2016/03/29/top-6-strange-motorcycle-noises-what-they-may-mean/ | EN06 |
| Honda Global, "The Importance of Periodic Replacement - Engine Oil", https://global.honda/en/motorcycle-aftersales/plusone/202303.html | EN06, EN16 |
| Honda Global, "You see all those different indicators on your bike's instrumentation?", https://global.honda/en/motorcycle-aftersales/plusone/202412.html | EN08 |
| Honda CBF500 owner's manual, "Coolant", https://www.bike-parts.fr/thumbs/pdf_url/img/owner_manuals/CBF500A5_E/2500_2500/0036.pdf | EN09, EN15 |
| Honda owner's manual (web edition), "Overheating (High coolant temperature indicator is on)", https://webom.hondamotopub.com/webom/HMEE/MLB250/html/GTS004001.html | EN10, EN18 |
| Mobil, "Proper throttle-body cleaning guide", https://www.mobil.com/en/lubricants/for-personal-vehicles/auto-care/vehicle-maintenance/how-to-do-it-yourself/proper-throttle-body-cleaning-guide | EN11 |
| Honda CBF250 owner's manual, "Idle Speed", https://www.bike-parts.fr/thumbs/pdf_url/img/owner_manuals/CBF2504_E/2500_2500/0073.pdf | EN12 |
| Honda CBF250 owner's manual, "Clutch", https://www.bike-parts.fr/thumbs/pdf_url/img/owner_manuals/CBF2504_E/2500_2500/0029.pdf | TR01, TR08, TR11 |
| Louis, "Scooter Variator and Clutch", https://www.louis.ie/en-ie/magazin/rund-ums-bike/schraubertipps/variomatik-und-kupplung | TR01, TR02, TR03, TR04, TR12 |
| Q9 PowerSports, "Scooter Drive Belt Replacement", https://q9powersportsusa.com/blogs/technical-support-q9-powersports-usa/change-drive-belt-motor-scooter | TR02, TR12 |
| T. Kimura et al., "A Study of Dry Centrifugal Clutch Judder", SAE Technical Paper 2005-32-0057, https://doi.org/10.4271/2005-32-0057 | TR04 |
| MCN, "Get your bite back: How to replace your clutch", https://motorcyclenews.com/news/members/week-4-how-to-clutch | TR05 |
| Honda owner's manual (web edition), "Drive Chain", https://webom.hondamotopub.com/webom/HMEE/MLB250/html/GMT018001.html | TR06, TR07, TR09 |
| Honda Global, "Ever wonder what happens if you don't conduct maintenance on your drive chain?", https://global.honda/en/motorcycle-aftersales/plusone/202306.html | TR06, TR10 |

Sổ tay Honda ở trên là của các mẫu xe bán ở nước ngoài; thông số (độ chùng xích, độ rơ tay côn) khác nhau theo mẫu xe, nên câu hỏi chỉ yêu cầu người lái so với sổ hướng dẫn của xe mình.

Mọi luật EN/TR đều đã có nguồn. Tất cả link được mở lại và đọc nội dung ngày 04/11/2026: nội dung khớp với luật. Link cũ `partzilla.com/blog/why/does/my/motorcycle/blow/blue/smoke/qa` đã chết (Page Not Found), nên EN07, EN13 chuyển sang trang Partzilla về màu khói.

Nguồn còn yếu, nên nói rõ trong báo cáo:
- EN06: Honda nói trễ thay nhớt một chút không gây tiếng kêu lạ; tiếng gõ thường do khe hở xu-páp. CF đã giảm từ 0.6 xuống 0.5.
- EN11: hướng dẫn của Mobil viết cho ô tô (họng ga hoạt động giống nhau).
- EN12: sổ tay Honda chỉ nói về chỉnh ga-răng-ti, không nói trực tiếp về chết máy.

## Khởi động, nhiên liệu (`starting_fuel.json`) và đánh lửa, điện (`ignition_electrical.json`) — Lâm

| Nguồn | Dùng cho luật |
|---|---|
| Honda, "PCX150 Owner's Manual" (2015), mục Starting the Engine và Troubleshooting: Engine Will Not Start, https://cdn.powersports.honda.com/documentum/MWOM/ml.remawmom.2015_31k36a00_pcx150.pdf | SF01, SF04, SF05, SF06, SF07, SF08, SF09, SF10, SF13, IE07 |
| Yuasa, "How to Know When to Replace a Powersports Battery", https://www.yuasabatteries.com/about/events-news/news/new-battery-when-to-replace/ | SF01, SF02, SF03, SF05, SF14 |
| Yuasa, "How Long is a Motorcycle Battery's Shelf Life?", https://www.yuasabatteries.com/resources/guides/motorcycle-batterys-shelf-life/ | SF03 |
| BikeBerry, "How to Diagnose a Flooded 2-Stroke Engine", https://www.bikeberry.com/blogs/learning-center/how-to-diagnose-a-flooded-2-stroke-engine | SF11 |
| Haynes, "8 Symptoms Of Motorcycle Fuel Pump Failure That Occur Before A Breakdown", https://us.haynes.com/blogs/tips-tutorials/8-symptoms-of-motorcycle-fuel-pump-failure-that-occur-before-a-breakdown | SF12 |
| E3 Spark Plugs, "8 Signs It's Time To Replace Your Motorcycle's Spark Plug", https://www.e3sparkplugs.com/blogs/news/8-signs-its-time-to-replace-your-motorcycles-spark-plug | IE01, IE02, IE03 |
| J.D. Power, "How To Know if Your Regulator-Rectifier Is Bad", https://www.jdpower.com/motorcycles/shopping-guides/how-to-know-if-regulator-rectifier-is-bad | IE04, IE05 |
| Eagle Lights, "How to Diagnose Motorcycle Lighting Problems", https://eaglelights.com/blogs/news/how-to-diagnose-motorcycle-lighting-problems | IE06, IE07 |

Mọi luật SF/IE đều đã có nguồn. Tất cả link được mở và đọc nội dung ngày 11/11/2026. Sổ tay PCX150 ghi: "The starter motor will only work when the rear brake lever is pulled and the side stand is up", và danh sách kiểm tra khi đề không quay gồm cầu chì, cọc bình lỏng hoặc gỉ, tình trạng ắc quy.

Nguồn còn yếu, nên nói rõ trong báo cáo:
- SF01: Yuasa nêu đèn và đồng hồ mờ là dấu hiệu ắc quy yếu, không nói riêng về còi; còi dùng điện ắc quy nên luật suy ra tương tự.
- SF02: Yuasa ghi ắc quy thường dùng 3–5 năm; mốc 2 năm của luật là để hỏi sớm, CF giữ 0.85 vì luật còn cần triệu chứng "điện yếu".
- SF08: sổ tay chỉ ghi đã kiểm tra hết mà đề vẫn không quay thì mang ra đại lý; việc quy cho rơ-le hoặc mô-tơ đề là suy luận của nhóm (CF 0.6).
- SF11: bài của BikeBerry viết cho động cơ 2 thì; hiện tượng ngộp xăng ở bình xăng con giống nhau.
- SF06: sổ tay chỉ nói kiểm tra cầu chì khi mất điện; điều kiện "mới thay ắc quy" là kinh nghiệm của nhóm.
- E3 Spark Plugs, Eagle Lights là trang của hãng bán phụ tùng, không phải sổ tay hãng xe.
- TR02, TR12: Q9 và Louis là trang bán phụ tùng, không phải sổ tay hãng.

## Tài liệu chung

1. S. Russell and P. Norvig, *Artificial Intelligence: A Modern Approach*, 4th ed., Pearson, 2020. Chapter 7: Logical Agents (PL-FC-ENTAILS?).
2. B. G. Buchanan and E. H. Shortliffe, *Rule-Based Expert Systems: The MYCIN Experiments of the Stanford Heuristic Programming Project*, Addison-Wesley, 1984 (certainty factor).
3. H. Wang, "Toward Mechanical Mathematics", *IBM Journal of Research and Development*, 4(1), 2–22, 1960 (thuật toán Wang).
