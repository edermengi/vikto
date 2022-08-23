-- noinspection SqlNoDataSourceInspectionForFile

-- The SQL to query "playable" words from Efremova's dictionary of Russian language
-- Dictionary is available for free https://reword.org/download/
select w.*, d.*
from words w
         join descriptions d on d.ROWID = w.ROWID
where (w.word NOT LIKE "...%")
  and (w.word NOT LIKE "-%")
  and (d.description NOT LIKE "несов%")
  and (d.description NOT LIKE "1. несов%")
  and (d.description NOT LIKE "сов%")
  and (d.description NOT LIKE "1. сов%")
  and (d.description NOT LIKE "суффикс%")
  and (d.description NOT LIKE "1. суффикс%")
  and (d.description NOT LIKE "союз%")
  and (d.description NOT LIKE "1. союз%")
  and (d.description NOT LIKE "префикс%")
  and (d.description NOT LIKE "1. префикс%")
  and (d.description NOT LIKE "предлог%")
  and (d.description NOT LIKE "1. предлог%")
  and (d.description NOT LIKE "мн.%")
  and (d.description NOT LIKE "союз%")
  and (d.description NOT LIKE "1. союз%")
  and (d.description NOT LIKE "<%")
  and (d.description NOT LIKE "%Соотнос%")
  and (d.description NOT LIKE "%по знач%")
  and (d.description NOT LIKE "%Уменьш.%")
  and (d.description NOT LIKE "%Женск. к сущ%")
  and (d.description NOT LIKE "%То же, что%")
  and (d.description NOT LIKE "%см. <%")
  and (d.description NOT LIKE "Начальная часть%")

