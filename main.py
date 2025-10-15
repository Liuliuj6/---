from toutiao_spider import ToutiaoSpider
import pandas as pd
import os


if __name__ == "__main__":
    spider = ToutiaoSpider()
    print("请输入要爬取的起始页数：")
    page_num_s = input()
    print("请输入要爬取的结束页数：")
    page_num_e = input()
    for i in range(int(page_num_s)-1,int(page_num_e)):
        toutiao_list = spider.search_toutiao(keyword='中传李雨珊', page=i)
        df = pd.DataFrame(toutiao_list)
        if os.path.exists("中传李雨珊.xlsx"):
            # 文件存在，读取现有数据
            try:
                existing_df = pd.read_excel("中传李雨珊.xlsx")

                # 将新旧数据合并
                updated_df = pd.concat([existing_df, df], ignore_index=True)
                updated_df.to_excel("中传李雨珊.xlsx", index=False)

            except Exception as e:
                print(f"读取或写入文件时发生错误：{e}")

        else:
            df.to_excel("中传李雨珊.xlsx", index=False)
    spider.driver_quit()
