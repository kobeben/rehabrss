import schedule
import time
from datetime import datetime
import sys
import os

# 添加项目路径
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, backend_dir)

from src.main import app
from src.models.user import db
from src.models.article import Article, News
from src.crawlers.pubmed_crawler import PubMedCrawler
from src.crawlers.scholar_crawler import ScholarCrawlerManager

class CrawlerScheduler:
    """爬虫调度器"""
    
    def __init__(self):
        self.pubmed_crawler = PubMedCrawler(email="rehab_news@example.com")
        self.scholar_manager = ScholarCrawlerManager()
        
        # 康复医学相关关键词
        self.rehab_keywords = [
            'rehabilitation',
            'physical therapy',
            'occupational therapy', 
            'stroke rehabilitation',
            'cardiac rehabilitation',
            'pulmonary rehabilitation',
            'orthopedic rehabilitation',
            'sports rehabilitation',
            'pediatric rehabilitation',
            'neurological rehabilitation'
        ]
    
    def crawl_and_save_articles(self):
        """爬取并保存文章到数据库"""
        print(f"开始爬取文章 - {datetime.now()}")
        
        with app.app_context():
            try:
                # 1. 从PubMed爬取文章
                print("正在从PubMed爬取文章...")
                pubmed_articles = self.pubmed_crawler.crawl_rehabilitation_articles(max_results=50)
                
                # 保存PubMed文章
                for article_data in pubmed_articles:
                    self._save_article_to_db(article_data)
                
                print(f"从PubMed保存了 {len(pubmed_articles)} 篇文章")
                
                # 2. 从其他学术搜索引擎爬取文章
                print("正在从其他学术搜索引擎爬取文章...")
                
                for keyword in self.rehab_keywords[:3]:  # 限制关键词数量以避免过度请求
                    try:
                        scholar_articles = self.scholar_manager.crawl_all_sources(
                            keyword, max_results_per_source=5
                        )
                        
                        # 保存学术搜索引擎文章
                        for article_data in scholar_articles:
                            self._save_article_to_db(article_data)
                        
                        print(f"关键词 '{keyword}' 保存了 {len(scholar_articles)} 篇文章")
                        
                        # 避免请求过于频繁
                        time.sleep(5)
                        
                    except Exception as e:
                        print(f"爬取关键词 '{keyword}' 时出错: {e}")
                        continue
                
                # 3. 生成一些示例新闻
                self._generate_sample_news()
                
                print(f"文章爬取完成 - {datetime.now()}")
                
            except Exception as e:
                print(f"爬取文章时出错: {e}")
    
    def _save_article_to_db(self, article_data: dict):
        """保存文章到数据库"""
        try:
            # 检查文章是否已存在（基于标题和来源）
            existing_article = Article.query.filter_by(
                title=article_data['title'],
                source=article_data['source']
            ).first()
            
            if existing_article:
                return  # 文章已存在，跳过
            
            # 创建新文章
            article = Article(
                title=article_data['title'],
                title_zh=self._translate_title(article_data['title']),  # 简单翻译
                category=article_data.get('category', '康复医学'),
                source=article_data['source'],
                url=article_data['url'],
                published_date=article_data['published_date']
            )
            
            db.session.add(article)
            db.session.commit()
            
        except Exception as e:
            print(f"保存文章到数据库时出错: {e}")
            db.session.rollback()
    
    def _translate_title(self, title: str) -> str:
        """简单的标题翻译（实际项目中可以使用翻译API）"""
        # 这里提供一些常见词汇的翻译映射
        translation_map = {
            'rehabilitation': '康复',
            'therapy': '治疗',
            'physical': '物理',
            'occupational': '作业',
            'stroke': '脑卒中',
            'cardiac': '心脏',
            'pulmonary': '肺部',
            'orthopedic': '骨科',
            'sports': '运动',
            'pediatric': '儿科',
            'neurological': '神经',
            'recovery': '恢复',
            'treatment': '治疗',
            'intervention': '干预',
            'exercise': '运动',
            'training': '训练'
        }
        
        # 简单替换（实际项目中建议使用专业翻译服务）
        translated = title.lower()
        for en_word, zh_word in translation_map.items():
            translated = translated.replace(en_word, zh_word)
        
        return translated.title()
    
    def _generate_sample_news(self):
        """生成一些示例新闻"""
        sample_news = [
            {
                'title': '康复医学新技术研讨会在京举办',
                'content': '近日，全国康复医学新技术研讨会在北京成功举办，来自全国各地的康复医学专家齐聚一堂，共同探讨康复医学领域的最新进展和技术创新。',
                'source': '康复医学网',
                'url': 'https://rehab-news.com/news1',
                'published_date': datetime.now()
            },
            {
                'title': '人工智能在康复治疗中的应用前景',
                'content': '随着人工智能技术的快速发展，其在康复治疗领域的应用也日益广泛。专家表示，AI技术将为康复治疗带来革命性的变化。',
                'source': '医疗科技日报',
                'url': 'https://medical-tech.com/news2',
                'published_date': datetime.now()
            }
        ]
        
        for news_data in sample_news:
            try:
                # 检查新闻是否已存在
                existing_news = News.query.filter_by(
                    title=news_data['title']
                ).first()
                
                if not existing_news:
                    news = News(**news_data)
                    db.session.add(news)
                    db.session.commit()
                    
            except Exception as e:
                print(f"保存新闻时出错: {e}")
                db.session.rollback()
    
    def start_scheduler(self):
        """启动定时任务调度器"""
        print("启动爬虫调度器...")
        
        # 设置定时任务
        schedule.every(6).hours.do(self.crawl_and_save_articles)  # 每6小时执行一次
        schedule.every().day.at("09:00").do(self.crawl_and_save_articles)  # 每天上午9点执行
        schedule.every().day.at("18:00").do(self.crawl_and_save_articles)  # 每天下午6点执行
        
        # 立即执行一次
        self.crawl_and_save_articles()
        
        # 持续运行调度器
        while True:
            schedule.run_pending()
            time.sleep(60)  # 每分钟检查一次

def run_crawler_once():
    """运行一次爬虫（用于测试）"""
    scheduler = CrawlerScheduler()
    scheduler.crawl_and_save_articles()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='康复医学文献爬虫')
    parser.add_argument('--once', action='store_true', help='只运行一次爬虫')
    parser.add_argument('--schedule', action='store_true', help='启动定时调度器')
    
    args = parser.parse_args()
    
    if args.once:
        run_crawler_once()
    elif args.schedule:
        scheduler = CrawlerScheduler()
        scheduler.start_scheduler()
    else:
        print("请指定运行模式：--once 或 --schedule")
        print("例如：python crawler_scheduler.py --once")

