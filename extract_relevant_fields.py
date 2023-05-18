def extract_relevant_fields(soup):
    intro = soup.find('div', {'class': 'pv-text-details__left-panel'})

    # Name
    name_loc = intro.find("h1")
    name = name_loc.get_text().strip()

    # Current workplace
    works_at_loc = intro.find("div", {'class': 'text-body-medium'})
    works_at = works_at_loc.get_text().strip()

    # Education
    education = []
    sections = soup.find_all('section')
    for section in sections:
        if section.find('div', {'id': 'education'}) is not None:
            ul = section.find('ul')
            for item in ul.find_all('li'):
                info_list = []
                for info in item.find_all('span', {'aria-hidden': 'true'}):
                    info_list.append(info.get_text().strip())
                education.append(info_list)

    
    row = {'Name': name, 'Workplace': works_at, 'Education': education}

    return row