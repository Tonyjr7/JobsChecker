class ProfileMatch:
    def profile_match(self, profile: str):
        devops = """solution architect,devops engineer,site reliability engineer,platform engineer,infrastructure engineer,cloud engineer,automation engineer,systems engineer,ci/cd engineer,operations engineer,solutions architect"""
        web = """software engineer,web developer,frontend developer,backend developer,full stack developer,software developer,senior software engineer,web application developer,javascript developer,python developer,java developer,react developer,angular developer,vue developer,node.js developer,ruby on rails developer,php developer"""
        data = """data scientist,machine learning engineer,ml engineer,ai engineer,data engineer,research scientist,applied scientist,data analyst,senior data scientist,machine learning researcher,deep learning engineer,nlp engineer,computer vision engineer,ai researcher,data science engineer,mlops engineer,ai/ml engineer,quantitative analyst,statistical analyst,predictive modeler,business intelligence engineer"""

        PROFILE_JOBS = {
            "devops": devops,
            "web": web,
            "data": data,
            "software engineer": web,
            "web developer": web,
            "data scientist": data,
            "machine learning engineer": data
        }

        profile_lower = profile.lower()
        relevant_jobs = None
        for key in PROFILE_JOBS:
            if key in profile_lower:
                relevant_jobs = PROFILE_JOBS[key]
                break

        if not relevant_jobs:
            relevant_jobs = web  # default

        foundational_jobs_keywords = [job.strip() for job in relevant_jobs.lower().split(",")]

        return foundational_jobs_keywords

match = ProfileMatch()
