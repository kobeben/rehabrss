import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import time
import sqlite3
import os
from typing import List, Dict, Optional

class PubMedCrawler:
    """PubMed文献爬虫类"""
    
    def __init__(self, email: str = "your_email@example.com"):
        self.base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
        self.email = email
        self.api_key = None  # 可选：注册NCBI API key以提高请求限制
        
    def search_articles(self, query: str, max_results: int = 100, days_back: int = 30) -> List[str]:
        """
        搜索PubMed文章并返回PMID列表
        
        Args:
            query: 搜索关键词
            max_results: 最大结果数
            days_back: 搜索最近多少天的文章
            
        Returns:
            PMID列表
        """
        # 构建日期范围查询
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        date_range = f"{start_date.strftime('%Y/%m/%d')}:{end_date.strftime('%Y/%m/%d')}[pdat]"
        
        # 构建完整查询
        full_query = f"({query}) AND {date_range}"
        
        # 构建搜索URL
        search_url = f"{self.base_url}esearch.fcgi"
        params = {
            'db': 'pubmed',
            'term': full_query,
            'retmax': max_results,
            'retmode': 'xml',
            'email': self.email,
            'sort': 'pub_date',  # 按发布日期排序
            'tool': 'rehab_news_crawler'
        }
        
        if self.api_key:
            params['api_key'] = self.api_key
            
        try:
            response = requests.get(search_url, params=params)
            response.raise_for_status()
            
            # 解析XML响应
            root = ET.fromstring(response.content)
            pmids = []
            
            for id_elem in root.findall('.//Id'):
                pmids.append(id_elem.text)
                
            return pmids
            
        except Exception as e:
            print(f"搜索文章时出错: {e}")
            return []
    
    def fetch_article_details(self, pmids: List[str]) -> List[Dict]:
        """
        获取文章详细信息
        
        Args:
            pmids: PMID列表
            
        Returns:
            文章详细信息列表
        """
        if not pmids:
            return []
            
        # 构建获取详情URL
        fetch_url = f"{self.base_url}efetch.fcgi"
        params = {
            'db': 'pubmed',
            'id': ','.join(pmids),
            'retmode': 'xml',
            'email': self.email,
            'tool': 'rehab_news_crawler'
        }
        
        if self.api_key:
            params['api_key'] = self.api_key
            
        try:
            response = requests.get(fetch_url, params=params)
            response.raise_for_status()
            
            # 解析XML响应
            root = ET.fromstring(response.content)
            articles = []
            
            for article in root.findall('.//PubmedArticle'):
                article_data = self._parse_article(article)
                if article_data:
                    articles.append(article_data)
                    
            return articles
            
        except Exception as e:
            print(f"获取文章详情时出错: {e}")
            return []
    
    def _parse_article(self, article_elem) -> Optional[Dict]:
        """解析单篇文章的XML数据"""
        try:
            # 获取PMID
            pmid_elem = article_elem.find('.//PMID')
            pmid = pmid_elem.text if pmid_elem is not None else None
            
            # 获取标题
            title_elem = article_elem.find('.//ArticleTitle')
            title = title_elem.text if title_elem is not None else "无标题"
            
            # 获取摘要
            abstract_elem = article_elem.find('.//AbstractText')
            abstract = abstract_elem.text if abstract_elem is not None else "无摘要"
            
            # 获取作者
            authors = []
            for author in article_elem.findall('.//Author'):
                lastname = author.find('LastName')
                forename = author.find('ForeName')
                if lastname is not None and forename is not None:
                    authors.append(f"{forename.text} {lastname.text}")
            
            # 获取发布日期
            pub_date = self._extract_publication_date(article_elem)
            
            # 获取期刊名称
            journal_elem = article_elem.find('.//Journal/Title')
            journal = journal_elem.text if journal_elem is not None else "未知期刊"
            
            # 构建PubMed URL
            url = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else ""
            
            return {
                'pmid': pmid,
                'title': title,
                'abstract': abstract,
                'authors': ', '.join(authors[:3]),  # 只取前3个作者
                'journal': journal,
                'published_date': pub_date,
                'url': url,
                'source': 'PubMed'
            }
            
        except Exception as e:
            print(f"解析文章时出错: {e}")
            return None
    
    def _extract_publication_date(self, article_elem) -> datetime:
        """提取发布日期"""
        try:
            # 尝试获取电子发布日期
            epub_date = article_elem.find('.//PubMedPubDate[@PubStatus="epublish"]')
            if epub_date is not None:
                year = epub_date.find('Year')
                month = epub_date.find('Month')
                day = epub_date.find('Day')
                
                if year is not None:
                    year_val = int(year.text)
                    month_val = int(month.text) if month is not None else 1
                    day_val = int(day.text) if day is not None else 1
                    return datetime(year_val, month_val, day_val)
            
            # 尝试获取期刊发布日期
            pub_date = article_elem.find('.//PubDate')
            if pub_date is not None:
                year = pub_date.find('Year')
                month = pub_date.find('Month')
                day = pub_date.find('Day')
                
                if year is not None:
                    year_val = int(year.text)
                    month_val = int(month.text) if month is not None else 1
                    day_val = int(day.text) if day is not None else 1
                    return datetime(year_val, month_val, day_val)
                    
        except Exception:
            pass
            
        # 默认返回当前日期
        return datetime.now()
    
    def crawl_rehabilitation_articles(self, max_results: int = 50) -> List[Dict]:
        """
        爬取康复医学相关文章
        
        Args:
            max_results: 最大结果数
            
        Returns:
            文章列表
        """
        # 康复医学相关关键词
        rehab_keywords = [
            "rehabilitation",
            "physical therapy", 
            "occupational therapy",
            "stroke rehabilitation",
            "neurological rehabilitation",
            "cardiac rehabilitation",
            "pulmonary rehabilitation",
            "orthopedic rehabilitation",
            "sports rehabilitation",
            "pediatric rehabilitation"
        ]
        
        all_articles = []
        
        for keyword in rehab_keywords:
            print(f"正在搜索关键词: {keyword}")
            
            # 搜索文章
            pmids = self.search_articles(keyword, max_results=max_results//len(rehab_keywords))
            
            if pmids:
                # 获取文章详情
                articles = self.fetch_article_details(pmids)
                
                # 为每篇文章添加分类
                for article in articles:
                    article['category'] = self._categorize_article(keyword)
                    
                all_articles.extend(articles)
                
                # 避免请求过于频繁
                time.sleep(1)
        
        # 按发布日期排序（最新的在前）
        all_articles.sort(key=lambda x: x['published_date'], reverse=True)
        
        # 去重（基于PMID）
        seen_pmids = set()
        unique_articles = []
        for article in all_articles:
            if article['pmid'] not in seen_pmids:
                seen_pmids.add(article['pmid'])
                unique_articles.append(article)
        
        return unique_articles
    
    def _categorize_article(self, keyword: str) -> str:
        """根据关键词对文章进行分类"""
        category_map = {
            "rehabilitation": "康复医学",
            "physical therapy": "物理治疗",
            "occupational therapy": "作业治疗", 
            "stroke rehabilitation": "神经康复",
            "neurological rehabilitation": "神经康复",
            "cardiac rehabilitation": "心肺康复",
            "pulmonary rehabilitation": "呼吸康复",
            "orthopedic rehabilitation": "骨科康复",
            "sports rehabilitation": "运动康复",
            "pediatric rehabilitation": "儿童康复"
        }
        
        return category_map.get(keyword, "康复医学")

# 使用示例
if __name__ == "__main__":
    crawler = PubMedCrawler(email="your_email@example.com")
    articles = crawler.crawl_rehabilitation_articles(max_results=20)
    
    for article in articles:
        print(f"标题: {article['title']}")
        print(f"分类: {article['category']}")
        print(f"发布日期: {article['published_date']}")
        print(f"URL: {article['url']}")
        print("-" * 50)

