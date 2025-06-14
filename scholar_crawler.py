import requests
from bs4 import BeautifulSoup
import time
import random
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import re

class ScholarCrawler:
    """学术搜索引擎爬虫基类"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def _random_delay(self, min_delay: float = 1.0, max_delay: float = 3.0):
        """随机延迟以避免被封"""
        time.sleep(random.uniform(min_delay, max_delay))

class GoogleScholarCrawler(ScholarCrawler):
    """Google Scholar爬虫"""
    
    def __init__(self):
        super().__init__()
        self.base_url = "https://scholar.google.com/scholar"
    
    def search_articles(self, query: str, max_results: int = 20) -> List[Dict]:
        """
        搜索Google Scholar文章
        
        Args:
            query: 搜索关键词
            max_results: 最大结果数
            
        Returns:
            文章列表
        """
        articles = []
        start = 0
        
        while len(articles) < max_results:
            params = {
                'q': query,
                'start': start,
                'hl': 'en',
                'as_sdt': '0,5'  # 包含专利和引用
            }
            
            try:
                response = self.session.get(self.base_url, params=params)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                results = soup.find_all('div', class_='gs_r gs_or gs_scl')
                
                if not results:
                    break
                
                for result in results:
                    if len(articles) >= max_results:
                        break
                        
                    article = self._parse_google_scholar_result(result)
                    if article:
                        articles.append(article)
                
                start += 10
                self._random_delay(2, 4)  # Google Scholar需要更长延迟
                
            except Exception as e:
                print(f"Google Scholar搜索出错: {e}")
                break
        
        return articles
    
    def _parse_google_scholar_result(self, result) -> Optional[Dict]:
        """解析Google Scholar搜索结果"""
        try:
            # 获取标题和链接
            title_elem = result.find('h3', class_='gs_rt')
            if not title_elem:
                return None
                
            title_link = title_elem.find('a')
            title = title_link.get_text() if title_link else title_elem.get_text()
            url = title_link.get('href') if title_link else ""
            
            # 获取作者和期刊信息
            authors_elem = result.find('div', class_='gs_a')
            authors_text = authors_elem.get_text() if authors_elem else ""
            
            # 解析作者和年份
            authors, year = self._parse_authors_and_year(authors_text)
            
            # 获取摘要
            snippet_elem = result.find('span', class_='gs_rs')
            snippet = snippet_elem.get_text() if snippet_elem else ""
            
            # 获取引用数
            cited_elem = result.find('a', string=re.compile(r'Cited by'))
            citations = 0
            if cited_elem:
                cited_text = cited_elem.get_text()
                citations_match = re.search(r'Cited by (\d+)', cited_text)
                if citations_match:
                    citations = int(citations_match.group(1))
            
            return {
                'title': title.strip(),
                'authors': authors,
                'abstract': snippet.strip(),
                'url': url,
                'published_date': self._parse_year_to_date(year),
                'citations': citations,
                'source': 'Google Scholar'
            }
            
        except Exception as e:
            print(f"解析Google Scholar结果时出错: {e}")
            return None
    
    def _parse_authors_and_year(self, authors_text: str) -> tuple:
        """从作者信息中解析作者和年份"""
        # 尝试提取年份
        year_match = re.search(r'\b(19|20)\d{2}\b', authors_text)
        year = int(year_match.group()) if year_match else datetime.now().year
        
        # 提取作者（通常在第一个破折号之前）
        authors_part = authors_text.split(' - ')[0] if ' - ' in authors_text else authors_text
        authors = authors_part.strip()
        
        return authors, year
    
    def _parse_year_to_date(self, year: int) -> datetime:
        """将年份转换为日期对象"""
        try:
            return datetime(year, 1, 1)
        except:
            return datetime.now()

class BaiduScholarCrawler(ScholarCrawler):
    """百度学术爬虫"""
    
    def __init__(self):
        super().__init__()
        self.base_url = "https://xueshu.baidu.com/s"
    
    def search_articles(self, query: str, max_results: int = 20) -> List[Dict]:
        """
        搜索百度学术文章
        
        Args:
            query: 搜索关键词
            max_results: 最大结果数
            
        Returns:
            文章列表
        """
        articles = []
        pn = 0  # 百度学术的分页参数
        
        while len(articles) < max_results:
            params = {
                'wd': query,
                'pn': pn,
                'tn': 'SE_baiduxueshu_c1gjeupa',
                'ie': 'utf-8',
                'sc_hit': '1'
            }
            
            try:
                response = self.session.get(self.base_url, params=params)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                results = soup.find_all('div', class_='result')
                
                if not results:
                    break
                
                for result in results:
                    if len(articles) >= max_results:
                        break
                        
                    article = self._parse_baidu_scholar_result(result)
                    if article:
                        articles.append(article)
                
                pn += 10
                self._random_delay(1, 2)
                
            except Exception as e:
                print(f"百度学术搜索出错: {e}")
                break
        
        return articles
    
    def _parse_baidu_scholar_result(self, result) -> Optional[Dict]:
        """解析百度学术搜索结果"""
        try:
            # 获取标题和链接
            title_elem = result.find('h3')
            if not title_elem:
                return None
                
            title_link = title_elem.find('a')
            title = title_link.get_text() if title_link else title_elem.get_text()
            url = title_link.get('href') if title_link else ""
            
            # 获取作者信息
            author_elem = result.find('p', class_='author')
            authors = author_elem.get_text() if author_elem else ""
            
            # 获取摘要
            abstract_elem = result.find('p', class_='abstract')
            abstract = abstract_elem.get_text() if abstract_elem else ""
            
            # 获取发布信息
            pub_elem = result.find('p', class_='kw')
            pub_info = pub_elem.get_text() if pub_elem else ""
            
            # 尝试从发布信息中提取年份
            year_match = re.search(r'\b(19|20)\d{2}\b', pub_info)
            year = int(year_match.group()) if year_match else datetime.now().year
            
            return {
                'title': title.strip(),
                'authors': authors.strip(),
                'abstract': abstract.strip(),
                'url': url,
                'published_date': datetime(year, 1, 1),
                'source': '百度学术'
            }
            
        except Exception as e:
            print(f"解析百度学术结果时出错: {e}")
            return None

class CNKICrawler(ScholarCrawler):
    """中国知网爬虫（简化版）"""
    
    def __init__(self):
        super().__init__()
        self.base_url = "https://kns.cnki.net/kns8/defaultresult/index"
    
    def search_articles(self, query: str, max_results: int = 20) -> List[Dict]:
        """
        搜索知网文章（注意：知网有严格的反爬机制，这里只是示例）
        
        Args:
            query: 搜索关键词
            max_results: 最大结果数
            
        Returns:
            文章列表
        """
        # 注意：实际使用时需要处理知网的登录和反爬机制
        # 这里提供一个基础框架
        
        articles = []
        
        # 由于知网的复杂性，这里返回模拟数据
        # 实际项目中建议使用知网的官方API或购买数据服务
        
        sample_articles = [
            {
                'title': f'康复医学相关研究 - {query}',
                'authors': '张三, 李四',
                'abstract': f'本研究探讨了{query}在康复医学中的应用...',
                'url': 'https://kns.cnki.net/example',
                'published_date': datetime.now() - timedelta(days=random.randint(1, 365)),
                'source': '中国知网'
            }
        ]
        
        return sample_articles[:max_results]

# 综合爬虫管理器
class ScholarCrawlerManager:
    """学术爬虫管理器"""
    
    def __init__(self):
        self.crawlers = {
            'google_scholar': GoogleScholarCrawler(),
            'baidu_scholar': BaiduScholarCrawler(),
            'cnki': CNKICrawler()
        }
    
    def crawl_all_sources(self, query: str, max_results_per_source: int = 10) -> List[Dict]:
        """
        从所有来源爬取文章
        
        Args:
            query: 搜索关键词
            max_results_per_source: 每个来源的最大结果数
            
        Returns:
            所有文章列表
        """
        all_articles = []
        
        for source_name, crawler in self.crawlers.items():
            print(f"正在从 {source_name} 爬取数据...")
            
            try:
                articles = crawler.search_articles(query, max_results_per_source)
                
                # 为每篇文章添加分类
                for article in articles:
                    article['category'] = self._categorize_article(query)
                
                all_articles.extend(articles)
                print(f"从 {source_name} 获取了 {len(articles)} 篇文章")
                
            except Exception as e:
                print(f"从 {source_name} 爬取数据时出错: {e}")
            
            # 在不同来源之间添加延迟
            time.sleep(2)
        
        # 按发布日期排序
        all_articles.sort(key=lambda x: x['published_date'], reverse=True)
        
        return all_articles
    
    def _categorize_article(self, query: str) -> str:
        """根据查询关键词对文章进行分类"""
        category_map = {
            'rehabilitation': '康复医学',
            'physical therapy': '物理治疗',
            'occupational therapy': '作业治疗',
            'stroke': '神经康复',
            'cardiac': '心肺康复',
            'pulmonary': '呼吸康复',
            'orthopedic': '骨科康复',
            'sports': '运动康复',
            'pediatric': '儿童康复'
        }
        
        query_lower = query.lower()
        for keyword, category in category_map.items():
            if keyword in query_lower:
                return category
        
        return '康复医学'

# 使用示例
if __name__ == "__main__":
    manager = ScholarCrawlerManager()
    
    # 康复医学相关关键词
    keywords = [
        'rehabilitation therapy',
        'physical therapy',
        'stroke rehabilitation',
        'cardiac rehabilitation'
    ]
    
    for keyword in keywords:
        print(f"\n搜索关键词: {keyword}")
        articles = manager.crawl_all_sources(keyword, max_results_per_source=5)
        
        for article in articles:
            print(f"标题: {article['title']}")
            print(f"来源: {article['source']}")
            print(f"分类: {article['category']}")
            print("-" * 50)

