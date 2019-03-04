-- schema for looking glass database
--
--

create table glasses (
    lgid                    integer primary key,
    last_checked            text,
    last_changed            text,    
    name                    text,
    asn                     integer,
    glass_url_source        text,
    glass_url_destination   text,
    protocol_source         text,
    protocol_destination    text,
    http_status             text,
    is_redirect             text,
    headers_count           integer,
    headers_bytes           integer,
    response_bytes          integer
);




