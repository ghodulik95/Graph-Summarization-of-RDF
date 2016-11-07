
SELECT s.s,s.p,s.o, COUNT(*) AS c
FROM
(
SELECT IIF([Subject] LIKE '%movie%', 'm', IIF([Subject] LIKE '%company%', 'c', IIF ([Subject] LIKE '%person%', 'p', 'other'))) AS s,
			 [Predicate]  AS p,
			 IIF([Object] LIKE '%movie%', 'm', IIF([Object] LIKE '%company%', 'c', IIF ([Object] LIKE '%person%', 'p', 'other'))) AS o
			  FROM [IMDBSmall].[dbo].[RDF]
			  WHERE [Object] NOT LIKE '%"%' AND [Object] NOT LIKE '%#%' AND [Object] LIKE '%<%' AND [Predicate] NOT LIKE '%#type%'
                AND [Object] LIKE '%[^0-9]%' AND [Subject] NOT LIKE '%"%' AND [Subject] LIKE '%[^0-9]%' AND [Object] NOT LIKE '%Disease_Annotation>%' ) s

				GROUP BY s.s,s.p,s.o
				ORDER BY c DESC