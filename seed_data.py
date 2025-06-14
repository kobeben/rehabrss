from datetime import datetime

def seed_sample_data(app, db, Article, News):
    """添加示例数据到数据库"""
    
    # 示例文章数据
    sample_articles = [
        {
            'title': 'Virtual Reality-Assisted Rehabilitation for Post-Stroke Motor Recovery: A Randomized Controlled Trial',
            'title_zh': '虚拟现实辅助康复治疗脑卒中后运动功能恢复的随机对照试验',
            'category': '神经康复',
            'source': 'PubMed',
            'url': 'https://pubmed.ncbi.nlm.nih.gov/example1',
            'published_date': datetime(2023, 10, 28)
        },
        {
            'title': 'Early Mobilization Protocols After Total Knee Replacement: Outcomes and Cost-Benefit Analysis',
            'title_zh': '全膝关节置换术后早期活动方案的临床结果与成本效益分析',
            'category': '骨科康复',
            'source': 'Google Scholar',
            'url': 'https://scholar.google.com/example2',
            'published_date': datetime(2023, 10, 26)
        },
        {
            'title': 'High-Intensity Interval Training vs Moderate Exercise in Cardiac Patients',
            'title_zh': '高强度间歇训练与传统中等强度训练在心脏康复患者中的比较研究',
            'category': '心肺康复',
            'source': '百度学术',
            'url': 'https://xueshu.baidu.com/example3',
            'published_date': datetime(2023, 10, 24)
        },
        {
            'title': 'Biomechanical Analysis of ACL Rehabilitation Protocols in Professional Athletes',
            'title_zh': '职业运动员前交叉韧带康复方案的生物力学分析',
            'category': '运动康复',
            'source': '中国知网',
            'url': 'https://cnki.net/example4',
            'published_date': datetime(2023, 10, 22)
        },
        {
            'title': 'Robot-Assisted Therapy in Pediatric Cerebral Palsy: A Meta-Analysis',
            'title_zh': '机器人辅助治疗在小儿脑瘫康复中的疗效：Meta分析',
            'category': '儿童康复',
            'source': 'PubMed',
            'url': 'https://pubmed.ncbi.nlm.nih.gov/example5',
            'published_date': datetime(2023, 10, 20)
        },
        {
            'title': 'Pulmonary Rehabilitation in Post-COVID Patients: Long-Term Efficacy Study',
            'title_zh': '新冠后遗症患者呼吸康复治疗长期疗效研究',
            'category': '呼吸康复',
            'source': 'Google Scholar',
            'url': 'https://scholar.google.com/example6',
            'published_date': datetime(2023, 10, 18)
        }
    ]
    
    # 示例新闻数据
    sample_news = [
        {
            'title': '国际康复医学大会将于明年在北京举办',
            'content': '据悉，第25届国际康复医学大会将于2024年5月在北京国际会议中心举办，预计将有来自全球50多个国家的康复医学专家参会，共同探讨康复医学的最新发展趋势和技术创新。',
            'source': '康复医学网',
            'url': 'https://rehab-news.com/example1',
            'published_date': datetime(2023, 10, 25)
        },
        {
            'title': '新型康复机器人获得FDA批准上市',
            'content': '美国食品药品监督管理局（FDA）近日批准了一款新型下肢康复机器人上市，该设备采用先进的人工智能算法，能够根据患者的康复进度自动调整训练强度和模式。',
            'source': '医疗器械新闻',
            'url': 'https://medical-device-news.com/example2',
            'published_date': datetime(2023, 10, 23)
        },
        {
            'title': '虚拟现实技术在康复治疗中的应用前景广阔',
            'content': '最新研究表明，虚拟现实技术在神经康复、疼痛管理和心理康复等领域展现出巨大潜力，多家医院已开始试点应用VR康复系统。',
            'source': '科技日报',
            'url': 'https://tech-daily.com/example3',
            'published_date': datetime(2023, 10, 21)
        }
    ]
    
    with app.app_context():
        # 清空现有数据
        Article.query.delete()
        News.query.delete()
        
        # 添加示例文章
        for article_data in sample_articles:
            article = Article(**article_data)
            db.session.add(article)
        
        # 添加示例新闻
        for news_data in sample_news:
            news = News(**news_data)
            db.session.add(news)
        
        db.session.commit()
        print(f"已添加 {len(sample_articles)} 篇文章和 {len(sample_news)} 条新闻到数据库")

if __name__ == '__main__':
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
    
    from src.main import app
    from src.models.user import db
    from src.models.article import Article, News
    
    seed_sample_data(app, db, Article, News)

