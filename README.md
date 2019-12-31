`isbnlib` as a microservice
===========================


This is **ALPHA** software!

>**Please** don't expose this service to the public web,
>use it only as a microservice inside your app.


To try it, you need to install Docker in your system and clone this repository.
Then enter in a terminal (inside directory `isbnsrv-master`):

```
$ docker build --tag="isbnsrv:0.0.1" .
$ docker run -d -p 8080:8080 isbnsrv:0.0.1
```

(it exposes port 8080).


Now in your browser go to:

```
http://localhost:8080/api/v1/isbns/9780375869020/metadata
http://localhost:8080/api/v1/isbns/9780375869020/metadata/openl
http://localhost:8080/api/v1/isbns/9780375869020/metadata/goob
http://localhost:8080/api/v1/isbns/9780375869020/isbn10
http://localhost:8080/api/v1/isbns/9780375869020/isbn13
http://localhost:8080/api/v1/isbns/9780375869020/info
http://localhost:8080/api/v1/isbns/9780375869020/mask
http://localhost:8080/api/v1/isbns/9780375869020/description
http://localhost:8080/api/v1/isbns/9780375869020/cover
http://localhost:8080/api/v1/isbns/9780375869020/editions
http://localhost:8080/api/v1/providers
```

**These are the main endpoints of the API**.


There his a **'bag' mode** too (some examples):

```
http://localhost:8080/api/v1/isbns/9780375869020
http://localhost:8080/api/v1/isbns/9780375869020?fields=metadata,openl
http://localhost:8080/api/v1/isbns/9780375869020?fields=isbn13,isbn10,mask,metadata,description
```

If you don't indicate any field (like in the first example above) all fields are
considered and the response is very slow. You should be very specific and
**choose the fields that you need**.

Bags are slow with fields `editions`, `cover`, `metadata` or `description` and fast with fields
`isbn10`, `isbn13`, `mask` or `info`.
