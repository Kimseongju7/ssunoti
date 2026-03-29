# from bs4 import BeautifulSoup
#
# session = rl.create_session()
# session = rl.login(session)
# if session.cookies.get_dict() != None:
#     print("SUCCESS")
# res = session.get("https://path.ssu.ac.kr/ptfol/imng/icmpNsbjtPgm/findIcmpNsbjtPgmList.do")
# soup = BeautifulSoup(res.text, 'lxml')
# print(soup.title.text)
# print(soup.select("div[class='lica_wrap'] > ul > li > div[class='cont_box'] > div[class='desc_wrap'] > div[class='text_wrap'] > a")[0].text)