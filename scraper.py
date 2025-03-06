import urllib
from urllib.parse import quote_plus, urlparse
from bs4 import BeautifulSoup
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from seleniumwire import webdriver
import json
import os
import xml.etree.ElementTree as ET
import pandas as pd
import openpyxl
import requests


class Scraper:
    total_page = 0
    per_page = 10
    cur_page = 0

    def init_web_driver(self):
        chrome_options = ChromeOptions()
        #  Optional argument to run the driver headlessly
        user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
        chrome_options.add_argument('user-agent=' + user_agent)
        chrome_options.add_argument("lang=ko_KR")
        chrome_options.add_argument('headless')
        chrome_options.add_argument('window-size=1920x1080')
        chrome_options.add_argument("disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        # 크롬 드라이버 최신 버전 설정
        service = ChromeService(executable_path="./chromedriver")
        return webdriver.Chrome(service=service, options=chrome_options)


    def binary_to_json(self, binary_data):
        """
        Decodes binary data as a string and converts it to JSON.

        Args:
        binary_data: Bytes representing the binary data.

        Returns:
        A dictionary or list representing the decoded JSON data,
        or None if1 decoding fails.
        """
        try:
            # Decode the binary data as a UTF-8 string
            string_data = binary_data.decode('utf-8')
            # Load the string data as JSON
            json_data = json.loads(string_data)
            return json_data
        except (UnicodeDecodeError, json.JSONDecodeError):
            # Handle potential decoding and parsing errors
            print("Error: Could not decode or parse the binary data as JSON.")
            return None

    def binary_to_xml(binary_data):
        """
        Simplified example: Assumes binary data represents a list of integers.

        Args:
            binary_data: Bytes object containing the binary data.

        Returns:
            str: XML string representing the data.
        """

        root = ET.Element("jobsList")
        for i in range(0, len(binary_data), 4):  # Assuming each integer is 4 bytes
            integer_value = int.from_bytes(binary_data[i:i + 4], byteorder='big')
            item = ET.SubElement(root, "item")
            item.text = str(integer_value)

        tree = ET.ElementTree(root)
        return ET.tostring(tree, encoding='utf-8').decode('utf-8')


    def extract_xml_to_excel(url, xml_tag, attribute, filename='data.xlsx'):
        """
        XML 파일에서 특정 요소를 추출하여 Excel 파일로 저장하는 함수

        Args:
            url (str): XML 파일 URL
            xml_tag (str): 추출할 XML 태그 이름
            attribute (str, optional): 추출할 속성 이름. Defaults to None.
            filename (str, optional): 저장할 Excel 파일 이름. Defaults to 'data.xlsx'.
        """

        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'lxml')

        data = []
        for element in soup.find_all(xml_tag):
            if attribute:
                data.append(element.get(attribute))
            else:
                data.append(element.text.strip())

        df = pd.DataFrame(data, columns=['Extracted Data'])
        df.to_excel(filename, index=False)


    def modify_response(self, request, response):
        print("요청 URL:", request.url)
        print("Content-Type:", request.headers["Content-Type"])
        print("XML 응답:", response.body)

        xml_data = self.binary_to_xml(response.body)

        # 파일 저장
        url = xml_data["dataBody"]["RESULT_LIST"][0]["PDF_FILE_NM"]
        print(url)
        filename = os.path.join(output_dir, os.path.basename(urlparse(url).path))

        urllib.request.urlretrieve(url, filename)


    def scraping(self):
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.append(['jobSmclNm', 'jobSum'])
        # filename
        filename = "job_info.xlsx"
        while 1:
            try:
                jobAPI = f"https://www.work24.go.kr/cm/openApi/call/wk/callOpenApiSvcInfo212L01.do?authKey=< Your API Key >&returnType=XML&target=JOBCD"
                url = jobAPI  ## + quote_plus(keyword)
                driver.get(url)

                xml = driver.page_source
                soup = BeautifulSoup(xml, features="xml")

                jobLists = soup.find_all("jobList")
                for jobList in jobLists:
                    data = []
                    jobDetailAPI = f"https://www.work24.go.kr/cm/openApi/call/wk/callOpenApiSvcInfo212D01.do?authKey=< Your API Key >&returnType=XML&target=JOBDTL&jobGb=1&jobCd={jobList.find("jobCd").text}&dtlGb=1"
                    url = jobDetailAPI  ## + quote_plus(keyword)
                    driver.get(url)
                    xml = driver.page_source
                    soup = BeautifulSoup(xml, features="xml")

                    ## 종료 조건 추가
                    if soup is None:
                        break

                    data.append(soup.find("jobSmclNm").text)
                    job_text = soup.find('jobSum').text
                    data.append(job_text)
                    print(job_text)
                    sheet.append(data)
                workbook.save(filename)
                break
            except TimeoutException:
                print("Loading took too much time!")


if __name__ == "__main__":
    output_dir = "//worknet_job_list"
    sc = Scraper()
    driver = sc.init_web_driver()
    sc.scraping()
    driver.close()
