import requests
import click

benelux = ["lu", "be", "nl"]
eu = ["at", "be", "bg", "hr", "cy", "cz", "dk", "ee", "fi", "fr", "de", "gr", "hu", "ie", "it", "lv" ,"lt", "lu", "mt", "nl", "pl", "pt", "ro", "sk", "si", "es", "se"] 
country_list = ["ad", "ae", "af", "ag", "ai", "al", "am", "ao", "ar", "as", "at", "au", "aw", "ax", "az", "ba", "bb", "bd", "be", "bf", "bg", "bh", "bi", "bj", "bl", "bm", "bn", "bo", "bq", "br", "bs", "bt", "bw", "by", "bz", "ca", "cd", "cf", "cg", "ch", "ci", "ck", "cl", "cm", "cn", "co", "cr", "cu", "cv", "cw", "cy", "cz", "de", "dj", "dk", "dm", "do", "dz", "ec", "ee", "eg", "er", "es", "et", "eu", "fi", "fj", "fk", "fm", "fo", "fr", "ga", "gb", "gd", "ge", "gf", "gg", "gh", "gi", "gl", "gm", "gn", "gp", "gq", "gr", "gt", "gu", "gw", "gy", "hk", "hn", "hr", "ht", "hu", "id", "ie", "il", "im", "in", "io", "iq", "ir", "is", "it", "je", "jm", "jo", "jp", "ke", "kg", "kh", "ki", "km", "kn", "kp", "kr", "kw", "ky", "kz", "la", "lb", "lc", "li", "lk", "lr", "ls", "lt", "lu", "lv", "ly", "ma", "mc", "md", "me", "mf", "mg", "mh", "mk", "ml", "mm", "mn", "mo", "mp", "mq", "mr", "ms", "mt", "mu", "mv", "mw", "mx", "my", "mz", "na", "nc", "ne", "nf", "ng", "ni", "nl", "no", "np", "nr", "nu", "nz", "om", "pa", "pe", "pf", "pg", "ph", "pk", "pl", "pm", "pr", "ps", "pt", "pw", "py", "qa", "re", "ro", "rs", "ru", "rw", "sa", "sb", "sc", "sd", "se", "sg", "si", "sk", "sl", "sm", "sn", "so", "sr", "ss", "st", "sv", "sx", "sy", "sz", "tc", "td", "tg", "th", "tj", "tk", "tl", "tm", "tn", "to", "tr", "tt", "tv", "tw", "tz", "ua", "ug", "us", "uy", "uz", "va", "vc", "ve", "vg", "vi", "vn", "vu", "wf", "ws", "ye", "yt", "za", "zm", "zw"]

country_groups = {
    "benelux": benelux,
    "eu": eu,
}

def fetch_ip_ranges(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to fetch data. Status code:", response.status_code)
        return None

def generate_table(ip_ranges, country, output_format):
    pf_rules = f"table <{country}_ips> persist\n"
    
    if ip_ranges:
        # Extract IPv4 and IPv6 addresses and add to the PF table
        ipv4_addresses = ip_ranges["subnets"]["ipv4"]
        ipv6_addresses = ip_ranges["subnets"]["ipv6"]
        
        # pf_rules = f"table <{country}_ips> const {{"
        
        # for i, ip in enumerate(ipv4_addresses + ipv6_addresses):
        #     if i+1 != len(ipv4_addresses + ipv6_addresses):
        #         pf_rules += f"{ip}, "
        #     else:
        #         pf_rules += f"{ip}"

        # pf_rules+= "}\n"


        if output_format == 'pf':
            pf_rules = f"table <{country}_ips> persist\n"
            pf_rules += f"table <{country}_ips> const {{" + ", ".join(ipv4_addresses + ipv6_addresses) + "}\n"
            return pf_rules
        elif output_format == 'cisco':
            cisco_rules = ""
            acl_name = f"{country}_ips"
            for ip in ipv4_addresses + ipv6_addresses:
                cisco_rules += f"permit ip {ip} any\n"
            return f"ip access-list extended {acl_name}\n{cisco_rules}"

    else:
        pf_rules = "Failed to generate PF rules due to data fetching error."
    
    return pf_rules

def generate_tables_for_group(group, output_format):
    pf_rules = ""
    for c in group:
        url = f"https://raw.githubusercontent.com/ipverse/rir-ip/master/country/{c}/aggregated.json"
        ip_ranges = fetch_ip_ranges(url)
        pf_rules += generate_table(ip_ranges, c, output_format)
        pf_rules += "\n"
    return pf_rules


@click.command()
@click.option('--country', required=True, type=click.Choice(['eu', 'benelux'] + country_list, case_sensitive=False), help='Specify the country code for which you want to create a table, or benelux, or eu.')
@click.option('--format', type=click.Choice(['pf', 'cisco'], case_sensitive=False), default='pf', help='Specify the format of the output. Default is pf.')
def cli(country, format):
    if country in country_groups:
        group = country_groups[country]
        pf_rules = generate_tables_for_group(group, format)
        print(pf_rules)
    else:
        url = f"https://raw.githubusercontent.com/ipverse/rir-ip/master/country/{country}/aggregated.json"
        ip_ranges = fetch_ip_ranges(url)
        pf_rules = generate_table(ip_ranges, country, format)
        print(pf_rules)

if __name__ == '__main__':
    cli()