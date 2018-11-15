from keystoneauth1.identity import v3
from keystoneauth1 import session


def getToken(ip, username, password, project_name, user_domain_id, project_domain_id):
    auth = v3.Password(auth_url="http://"+ip+":5000/v3", username=username, password=password,
                       project_name=project_name, user_domain_id=user_domain_id, project_domain_id=project_domain_id)
    sess = session.Session(auth=auth)
    return sess.get_token(auth)