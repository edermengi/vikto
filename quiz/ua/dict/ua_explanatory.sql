-- noinspection SqlNoDataSourceInspectionForFile

-- The SQL to query "playable" words from explanatory dictionary of Ukranian language
-- Dictionary is available for free at https://reword.org/download/
SELECT tmp.word,
--        tmp.orig_description,
       REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(
                                                                                                                       SUBSTR(tmp.descr, INSTR(tmp.descr, "<i>")),
                                                                                                                       "<BR>",
                                                                                                                       ""),
                                                                                                               "</BR>",
                                                                                                               ""),
                                                                                                       "<i>", ""),
                                                                                               "</i>", ""),
                                                                                       "<b>", ""),
                                                                               "</b>", ""),
                                                                       "<br>", ""),
                                                               "</br>", ""),
                                                       "&acute;", ""),
                                               " 1.", "<br>1."),
                                       " 2.", "<br>2."),
                               " 3.", "<br>3."),
                       " 4.", "<br>4."),
               " 5.", "<br>5.")
           as description
FROM (SELECT word,
             orig_description,
             IIF(INSTR(descr, "&bull;") > 0, SUBSTR(descr, 0, INSTR(descr, "&bull;")), descr) as descr
      FROM (SELECT w.word,
                   d.description                                               as orig_description,
                   SUBSTR(d.description, INSTR(d.description, "<BR><BR>") + 8) as descr
            FROM words w
                     join descriptions d on d.ROWID = w.ROWID
            WHERE (w.word <> "")
              and (d.description NOT LIKE "%<7>%"))) as tmp
