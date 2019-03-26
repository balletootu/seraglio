mongoexport --db seraglio --collection model \
    --sort '{_id: 1}' \
    --pretty --out database/models.json
mongoexport --db seraglio --collection model_page \
    --sort '{_id: 1}' \
    --pretty --out database/model_pages.json
mongoexport --db seraglio --collection gallery \
    --sort '{site: 1, date: 1, _id: 1}' \
    --pretty --out database/galleries.json
mongoexport --db seraglio --collection the_nude_page \
    --sort '{_id: 1}' \
    --pretty --out database/thenude_pages.json
mongoexport --db seraglio --collection the_nude_gallery \
    --sort '{site: 1, date: 1, _id: 1}' \
    --pretty --out database/thenude_galleries.json
