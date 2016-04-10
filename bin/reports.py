#=============================
# Unitdate report generation
#============================
def report_dates(root):
    result = []
    
    allowed_patterns = [r'^\d{4}$', 
                        r'^\d{4}-\d{4}$', 
                        r'^[a-zA-Z]+? \d\d?,? \d{4}$',
                        r'^[a-zA-Z]+? \d\d?,? \d{4}-[a-zA-Z]+? \d\d?,? \d{4}$']
    
    unitdates = root.xpath(
        "//archdesc[@level='collection' and @type='combined']/did/unitdate")
    
    for u in unitdates:
        # strip out unitdates that have a null value
        if u.text == "null":
            u.getparent().remove(u)
            continue
    
        for p in allowed_patterns:
            if re.match(p, u.text):
                # print("{0} matches pattern {1}".format(u.text, p))
                continue
        else:
            result.append(u.text)
    
    return result


#=============================
# Extent report generation
#============================
def report_extents(root):
    result = []
    allowed_patterns = [r'^[0-9.]+ linear feet$']
    extents = root.find(".//physdesc")
    
    for e in extents:
        for p in allowed_patterns:
            if re.match(p, e.text):
                # print("{0} matches pattern {1}".format(e.text, p))
                break
        else:
            result.append(e.text)
    
    return result


dates = []
extents = []
    
# write out reports
if dates:
    with open('data/reports/unitdates_report.csv', 'w') as datesfile:
        datesfile.writelines("\n".join(dates))
    
if extents:
    with open('data/reports/extents_report.csv', 'w') as extentsfile:
        extentsfile.writelines("\n".join(extents))

