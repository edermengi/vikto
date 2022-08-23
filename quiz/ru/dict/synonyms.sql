-- noinspection SqlNoDataSourceInspectionForFile

-- The SQL to query "playable" words from synonym's dictionary of Russian language
-- Dictionary is available for free https://reword.org/download/
select w.word,
--     d.description   as orig_description,
       lower(w.word) || ", " || IIF(INSTR(d.description, ".") > 0, SUBSTR(d.description, 0, INSTR(d.description, ".")),
                                    d.description) as descrption
from words w
         join descriptions d on d.ROWID = w.ROWID
where (w.word NOT LIKE "...%")
  and (w.word NOT LIKE "-%")
  and (d.description NOT LIKE "см. <7>%")
  and (d.description NOT LIKE "||%")
  and (d.description NOT LIKE "<P>%")
  and (d.description NOT LIKE "[%")
  and (d.description NOT LIKE "(%")

