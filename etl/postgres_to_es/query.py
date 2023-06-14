from typing import Optional


def get_movies_query(modified: Optional[str]) -> str:
    """
    Формирует sql запрос с подставленной временной меткой для индекса movies
    """
    return f"""
    SELECT
        film.id,
        film.rating AS imdb_rating,
        film.title,
        film.description,
        ARRAY_AGG(DISTINCT genre.name) AS genre,
        ARRAY_AGG(DISTINCT jsonb_build_object('id', person.id, 'name', person.full_name))
            FILTER (WHERE person_film.role = 'director') AS director,
        ARRAY_AGG(DISTINCT person.full_name) FILTER (WHERE person_film.role = 'actor') AS actors_names,
        ARRAY_AGG(DISTINCT person.full_name) FILTER (WHERE person_film.role = 'writer') AS writers_names,
        ARRAY_AGG(DISTINCT jsonb_build_object('id', person.id, 'name', person.full_name))
            FILTER (WHERE person_film.role = 'actor') AS actors,
        ARRAY_AGG(DISTINCT jsonb_build_object('id', person.id, 'name', person.full_name))
            FILTER (WHERE person_film.role = 'writer') AS writers,
        GREATEST(film.modified, MAX(person.modified), MAX(genre.modified)) AS modified
    FROM content.film_work film
        LEFT JOIN content.genre_film_work AS genre_film ON film.id = genre_film.film_work_id
        LEFT JOIN content.genre AS genre ON genre_film.genre_id = genre.id
        LEFT JOIN content.person_film_work AS person_film ON film.id = person_film.film_work_id
        LEFT JOIN content.person AS person ON person_film.person_id = person.id
    WHERE
        GREATEST(film.modified, person.modified, genre.modified) > '{modified}'
    GROUP BY film.id
    ORDER BY GREATEST(film.modified, MAX(person.modified), MAX(genre.modified)) ASC;
    """


def get_persons_query(modified: Optional[str]) -> str:
    """
    Формирует sql запрос с подставленной временной меткой для индекса persons
    """
    return f"""
    SELECT
    person.id,
    person.full_name,
    ARRAY_AGG(jsonb_build_object('id', films.id, 'title', films.title, 'roles', films.roles)) AS films,
    GREATEST(MAX(films.modified), MAX(person.modified)) as modified
    FROM content.person person
    LEFT JOIN (
        SELECT film.id, film.title, person_film.person_id, ARRAY_AGG(DISTINCT person_film.role) as roles, film.modified
        FROM content.film_work film
        LEFT JOIN content.person_film_work person_film ON film.id = person_film.film_work_id
        GROUP BY film.id, person_film.person_id
    ) films ON person.id = films.person_id
    WHERE
        GREATEST(films.modified, person.modified) > '{modified}'
    GROUP BY person.id
    ORDER BY GREATEST(MAX(films.modified), MAX(person.modified)) ASC;
    """


def get_genres_query(modified: Optional[str]) -> str:
    """
    Формирует sql запрос с подставленной временной меткой для индекса genres
    """
    return f"""
    SELECT DISTINCT genre.id, genre.name, genre.modified FROM content.genre as genre
    WHERE genre.modified > '{modified}'
    ORDER BY genre.modified ASC;
    """


def get_query(modified: str, query_type: str) -> str:
    """
    Получает необходимый запрос
    """
    if query_type == 'movies':
        return get_movies_query(modified)
    elif query_type == 'persons':
        return get_persons_query(modified)
    elif query_type == 'genres':
        return get_genres_query(modified)
    else:
        return None
