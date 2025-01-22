#!/usr/bin/env python
# coding: utf-8

import requests, time, json, hashlib, argparse, sys
import urllib.parse as urllib
from requests.packages import urllib3
from urllib.parse import urlparse
from fake_useragent import UserAgent
from bs4 import BeautifulSoup

Welcome1 = r"""  ___      _        _                _        ___ _         _         """
Welcome2 = r""" / __|_  _| |__  __| |___ _ __  __ _(_)_ _   | __(_)_ _  __| |___ _ _ """
Welcome3 = r""" \__ \ || | '_ \/ _` / _ \ '  \/ _` | | ' \  | _|| | ' \/ _` / -_) '_|"""
Welcome4 = r""" |___/\_,_|_.__/\__,_\___/_|_|_\__,_|_|_||_| |_| |_|_||_\__,_\___|_|  """

Information = r"""
 Author: 	Threezh1
 Blog:		http://www.threezh1.com/
 Version:	1.0"""

Help = r"""
 Uage: README.md
 Stop searching: Ctrl + C
"""

urllib3.disable_warnings()
ua = UserAgent()
header = {"User-Agent": ua.chrome}
#header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.108 Safari/537.36"}

def parse_args():
    parser = argparse.ArgumentParser(epilog='\tExample: \r\npython ' + sys.argv[0] + " -d baidu.com")
    parser.add_argument("-d", "--domain", help="Domain name to enumerate subdomains of", required=True)
    parser.add_argument("-o", "--output", help="Output file name , By default, the domain name is the file_name.txt", action="store_true")
    parser.add_argument("-html", "--html", help="Output html, the domain name is the file_name.html", action="store_true")
    return parser.parse_args()

def get_domain_from_natcraft(domain):
	print("Get domains from natcraft... (Need some time)")
	part_subdomains = []
	page_count = 1
	have_content = True
	last_domain = ""
	while have_content:
		response = requests.get("https://searchdns.netcraft.com/", headers = header, verify = False, timeout = 10)
		temp_headers = response.headers
		if 'set-cookie' in temp_headers:
			""" This section of getting a cookie is taken from Sublist3r """
			temp_cookie = temp_headers['set-cookie']
			temp_cookies = dict()
			temp_cookies_list =  temp_cookie[0:temp_cookie.find(';')].split("=")
			temp_cookies[temp_cookies_list[0]] = temp_cookies_list[1]
			temp_cookies["netcraft_js_verification_response"] = hashlib.sha1(urllib.unquote(temp_cookies_list[1]).encode('utf-8')).hexdigest()
		url = 'https://searchdns.netcraft.com/?host=.{domain}&last={last_domain}&from={page}&restriction=site%20contains&position='.format(domain=domain, page = page_count, last_domain = last_domain)
		last_domain = ""
		try:
			data_raw = requests.get(url, headers = header, cookies = temp_cookies, verify = False, timeout = 10)
			data_content = data_raw.content.decode("utf-8", "ignore")
			data_html = BeautifulSoup(data_content, 'html.parser')
		except Exception as e:
			print(e)
			return part_subdomains
		try:
			html_divs = data_html.findAll("div", {"class": "blogbody"})
			html_ps = html_divs[1].findAll("p")
			html_ps_a = html_ps[1].find("a")
			last_domain = html_ps_a.get("href")[html_ps_a.get("href").find("last=") + 5:html_ps_a.get("href").find("&from=")]
		except Exception as e:
			have_content = False
		if last_domain == "": have_content = False
		try:
			html_table = data_html.find("table", {"class": "TBtable"})
			html_as = html_table.findAll("a", {"rel": "nofollow"})
		except Exception as e:
			print(e)
			continue
		for html_a in html_as:
			subdomian = html_a.get_text()
			if subdomian != "" and subdomian not in part_subdomains:
				part_subdomains.append(subdomian)
		page_count += 20
		time.sleep(3)
	return part_subdomains

def get_domain_from_ask(domain):
	print("Get domains from ask... (Need some time)")
	part_subdomains = []
	have_content = True
	page_count = 1
	while have_content:
		url = "https://www.ask.com/web?o=0&l=dir&qo=pagination&q=site:*.{domain}&qsrc=998&page={page}".format(domain = domain, page = page_count)
		try:
			data_raw = requests.get(url, headers = header, verify = False, timeout = 10)
			data_content = data_raw.content.decode("utf-8", "ignore")
			data_html = BeautifulSoup(data_content, 'html.parser')
			html_ps = data_html.findAll("p", {"class": "PartialSearchResults-item-url"})
		except Exception as e:
			print(e)
			return part_subdomains
		if len(html_ps) == 0:
			have_content = False
			continue
		for html_p in html_ps:
			url = "http://" + html_p.get_text()
			parsed = urlparse(url)
			parsed_domain = parsed.netloc
			if parsed_domain not in part_subdomains:
				part_subdomains.append(parsed_domain)
		page_count += 1
	return part_subdomains

def get_domain_from_baidu(domain):
	print("Get domains from baidu... (Need some time)")
	part_subdomains = []
	have_content = True
	page_count = 0
	while page_count < 200:
		url = "https://www.baidu.com/s?wd=site%3A{domain}&pn={page}".format(domain = domain, page = page_count)
		try:
			data_raw = requests.get(url, headers = header, verify = False, timeout = 10)
			data_content = data_raw.content.decode("utf-8", "ignore")
			data_html = BeautifulSoup(data_content, 'html.parser')
			html_as = data_html.findAll("a", {"class": "c-showurl"})
		except Exception as e:
			print(e)
			return part_subdomains
		temp_page = []
		for html_a in html_as:
			parsed = urlparse(html_a.get_text())
			parsed_domain = parsed.netloc
			if parsed_domain not in part_subdomains and parsed_domain != "":
				part_subdomains.append(parsed_domain)
		page_count += 10
	return part_subdomains

def get_domain_from_so(domain):
	print("Get domains from so... (Need some time)")
	part_subdomains = []
	have_content = True
	page_count = 0
	while page_count < 20:
		url = "https://www.so.com/s?q=site%3A{domain}&pn={page}&psid=8ce82e610522aff397e88b1f2604330f&src=srp_paging&fr=none".format(domain = domain, page = page_count)
		try:
			data_raw = requests.get(url, headers = header, verify = False, timeout = 10)
			data_content = data_raw.content.decode("utf-8", "ignore")
			data_html = BeautifulSoup(data_content, 'html.parser')
			html_ps = data_html.findAll("p", {"class": "res-linkinfo"})
		except Exception as e:
			print(e)
			return part_subdomains
		for html_p in html_ps:
			html_cite = html_p.find("cite")
			parsed = urlparse("http://" + html_cite.get_text())
			parsed_domain = parsed.netloc
			if parsed_domain.find(">") != -1:
				parsed_domain = parsed_domain[0:parsed_domain.find(">")]
			if parsed_domain not in part_subdomains and parsed_domain != "":
				part_subdomains.append(parsed_domain)
		page_count += 1
	return part_subdomains

def printx(content, color):
	colors = {
		"black": "30",
		"red": "31",
		"green": "32",
		"yellow": "33",
		"blue": "34",
		"fuchsia": "35",
		"cyan": "36",
		"white": "37"
	}
	if color not in colors:
		print(content)
	else:
		print("\033[1;{1};40m{0}\033[0m".format(content, colors[color]))

def GetDomainStatu(domain):
	import requests
	header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:63.0) Gecko/20100101 Firefox/63.0"}
	try:
		result = requests.get("http://{0}/".format(domain), headers = header, timeout = 10)
	except:
		return ""
	return str(result.status_code)

def GetUrlTitle(url):
	try:
		data_raw = requests.get(url,  headers = header, verify = False, timeout = 10)
		data_content = data_raw.content.decode("utf-8", "ignore")
		data_html = BeautifulSoup(data_content, 'html.parser')
		return data_html.title.get_text().strip()
	except:
		return ""

def subdomain_finder(domain):
	subdomains = []
	temp_subdomains = []
	try:
		temp_subdomains.append(get_domain_from_natcraft(domain))
		temp_subdomains.append(get_domain_from_ask(domain))
		temp_subdomains.append(get_domain_from_baidu(domain))
		temp_subdomains.append(get_domain_from_so(domain))
	except KeyboardInterrupt:
		pass
	except Exception as e:
		print(e)
		pass
	for temp_subdomain in temp_subdomains:
		if temp_subdomain == None or temp_subdomain == []: continue
		for subdomain_raw in temp_subdomain:
			subdomain = subdomain_raw.strip()
			subdomain = subdomain_raw.strip(".")
			if subdomain.find("*") != -1: subdomain = subdomain[2:]
			if subdomain is not None and subdomain != "" and domain in subdomain and subdomain not in subdomains:
				subdomains.append(subdomain)
	return subdomains

def process_domains(domain, subdomains, mode = "html"):
	temp_subdomains = list(set(subdomains))
	temp_subdomains.sort()
	if mode == "html":
		printx("A total of {0} subdomains need to be processed\n".format(str(len(subdomains))), "green")
		with open(domain.replace(".", "_") + ".html", "w", encoding='utf-8') as fobject:
			html = '<!DOCTYPE html>\n<html>\n<head>\n<title>{title}</title>\n'.format(title = domain)
			html += '<link rel="stylesheet" href="./css/style.css">\n</head>'
			html += '<body>\n<p class="domain" align="center">{domain}</p><table class="imagetable" align="center">\n'.format(domain=domain)
			html += '<tr>\n<th>id</th>\n<th>subdomain</th>\n<th>site</th>\n<th>title</th>\n<th>ip</th>\n<th>statu</th>\n</tr>'
			fobject.write(html)
			domain_id = 1
			for subdomain in temp_subdomains:
				domain_statu = GetDomainStatu(subdomain)
				domain_url = "http://{0}".format(subdomain)
				domain_title = GetUrlTitle(domain_url)
				print(" {id} : {subdomain} {title} {ip} {statu} ".format(id=str(domain_id), subdomain=subdomain, title=domain_title, statu=domain_statu))
				fobject.write("<tr>\n<td>{id}</td>\n<td>{subdomain}</td>\n<td>{site}</td>\n<td>{title}</td>\n<td>{ip}</td>\n<td>{statu}</td>\n</tr>".format(id=str(domain_id), subdomain=subdomain, site='<a target="_blank" href="{link}">{name}</a>'.format(link=domain_url, name=subdomain), title=domain_title, statu=domain_statu))
				domain_id += 1
			fobject.write("</table>\n</body>\n</html>")
		printx("\nOutput to file: {0}\n".format(domain.replace(".", "_") + ".html"), "green")

if __name__ == "__main__":
	printx(Welcome1, "red")
	printx(Welcome2, "yellow")
	printx(Welcome3, "green")
	printx(Welcome4, "cyan")
	printx(Information, "cyan")
	print(Help)
	args = parse_args()
	domain = args.domain
	printx("domain: {0}\n".format(domain), "green")
	subdomains = subdomain_finder(domain)
	printx("\nFound a total of {0} subdomains\n".format(str(len(subdomains))), "green")
	for subdomain in subdomains:
		print(subdomain)
	if args.output == True:
		output_name = domain.replace(".", "_") + ".txt"
		with open(output_name, "w", encoding='utf-8') as file_object:
			for subdomain in subdomains:
				file_object.write(subdomain + "\n")
		printx("\nOutput to file: {0}\n".format(output_name), "green")
	if args.html == True:
		process_domains(domain, subdomains, "html")
