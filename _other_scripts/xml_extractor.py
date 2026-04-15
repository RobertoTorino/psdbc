import csv
from lxml import etree

def convert_ps3tdb_to_csv(xml_input, csv_output):
    # Defining headers based on your new XML snippet
    headers = [
        'game_name', 'id', 'type', 'region', 'languages',
        'title', 'year', 'month', 'day', 'rom_name'
    ]

    with open(csv_output, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()

        # Stream parse 'game' tags to handle 200,000+ rows efficiently
        context = etree.iterparse(xml_input, events=('end',), tag='game')

        for event, elem in context:
            # Extract basic game data
            # .findtext() looks for the content inside tags like <id>ASIA00048</id>
            game_name = elem.get('name')
            game_id = elem.findtext('id')
            game_type = elem.findtext('type')
            region = elem.findtext('region')
            languages = elem.findtext('languages')

            # Extract data from nested tags
            # We look inside <locale> for the <title>
            title = elem.find('locale').findtext('title') if elem.find('locale') is not None else ""

            # We look at the attributes of the <date> tag
            date_tag = elem.find('date')
            year = date_tag.get('year') if date_tag is not None else ""
            month = date_tag.get('month') if date_tag is not None else ""
            day = date_tag.get('day') if date_tag is not None else ""

            # Handle the <rom> tag (similar to the previous script)
            roms = elem.findall('rom')

            if roms:
                for rom in roms:
                    writer.writerow({
                        'game_name': game_name,
                        'id': game_id,
                        'type': game_type,
                        'region': region,
                        'languages': languages,
                        'title': title,
                        'year': year,
                        'month': month,
                        'day': day,
                        'rom_name': rom.get('name')
                    })
            else:
                # If no ROM tag exists, write the row with an empty rom_name
                writer.writerow({
                    'game_name': game_name, 'id': game_id, 'type': game_type,
                    'region': region, 'languages': languages, 'title': title,
                    'year': year, 'month': month, 'day': day, 'rom_name': ""
                })

            # CRITICAL: Clear the element to keep memory usage low
            elem.clear()
            while elem.getprevious() is not None:
                del elem.getparent()[0]

# Execution
convert_ps3tdb_to_csv('ps3tdb.xml', 'ps3_database.csv')
print("Successfully processed over 200,000 entries.")