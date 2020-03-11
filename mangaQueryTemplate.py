manga_query = '''
query ($search: String) {
    Media(search: $search, type: MANGA) {
        chapters
        volumes
        status
        averageScore    
        startDate {
            year
            month
            day
        }
        endDate {
            year 
            month
            day
        }     
        genres
        title {
            romaji
            english
            native
        }
        description(asHtml:false)
        coverImage {
            large
        }
        id
    }
}
'''