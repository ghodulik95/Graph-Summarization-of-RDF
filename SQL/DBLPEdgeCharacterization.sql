/****** Script for SelectTopNRows command from SSMS  ******/

SELECT s.s,s.p,s.o, COUNT(*) AS c
FROM 
(
SELECT s = CASE 
			WHEN [Subject] LIKE '%books%' THEN 'book'
			WHEN [Subject] LIKE '%journals-%' OR [Subject] LIKE '%journal-' THEN 'journal'
			WHEN [Subject] LIKE '%journals/%' THEN 'article'
			WHEN [Subject] LIKE '%people%' THEN 'person'
			WHEN [Subject] LIKE '%conf%' THEN 'conference proceedings'
			WHEN [Subject] LIKE '%organization-%' THEN 'organization'
			WHEN [Subject] LIKE '%<http://dblp.rkbexplorer.com/id/tr/%' THEN 'article'
			WHEN [Subject] LIKE '%reference%' THEN 'reference'
			WHEN [Subject] LIKE '%publication%' THEN 'publication'
			WHEN [Predicate] LIKE '%#has-author%' THEN 'something authored'
			ELSE 'article'
		END,
			 [Predicate]  AS p,
	  o = CASE 
			WHEN [Object] LIKE '%people%' THEN 'person'
			WHEN [Object] LIKE '%books%' THEN 'book'
			WHEN [Object] LIKE '%journals-%' OR [Object] LIKE '%journal-%' THEN 'journal'
			WHEN [Object] LIKE '%journals/%' THEN 'article'
			WHEN [Object] LIKE '%conf%' THEN 'conference proceedings'
			WHEN [Object] LIKE '%organization-%' THEN 'organization'
			WHEN [Object] LIKE '%<http://dblp.rkbexplorer.com/id/tr/%' THEN 'article'
			WHEN [Object] LIKE '%reference%' THEN 'reference'
			WHEN [Object] LIKE '%publication%' THEN 'publication'
			ELSE 'article'
		END
			  FROM [DBLP4].[dbo].[RDF]
			  WHERE [Object] NOT LIKE '%"%' AND [Object] NOT LIKE '%#%' AND [Object] LIKE '%<%' AND [Predicate] NOT LIKE '%#type%'
                AND [Object] LIKE '%[^0-9]%' AND [Subject] NOT LIKE '%"%' AND [Subject] LIKE '%[^0-9]%' AND [Object] NOT LIKE '%Disease_Annotation>%' ) s

				GROUP BY s.s,s.p,s.o
				ORDER BY c DESC