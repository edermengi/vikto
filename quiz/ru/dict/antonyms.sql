-- noinspection SqlNoDataSourceInspectionForFile

-- The SQL to query antonyms from the dicationary of Russian synonyms
-- Dictionary is available for free at https://reword.org/download/
SELECT tmp.word,
--        tmp.orig_description,
       REPLACE(tmp.descr, " и ", ", ")
           as description
FROM (SELECT word,
             orig_description,
             SUBSTR(descr, 0, INSTR(descr, ">")) as descr
      FROM (SELECT w.word,
                   d.description                                              as orig_description,
                   SUBSTR(d.description, INSTR(d.description, "Прот. <") + 7) as descr
            FROM words w
                     join descriptions d on d.ROWID = w.ROWID
            WHERE (w.word <> "")
              and (d.description LIKE "%Прот. <%"))) as tmp
