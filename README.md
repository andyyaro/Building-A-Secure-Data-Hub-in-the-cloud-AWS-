![image1.png](word_fromPDF_v6_images/image1.png)

# Building A Secure Data Hub



Yiguedan Philippe Andy Yaro



View PortfolioView Techinal Blog


# ![image2.png](word_fromPDF_v6_images/image2.png)Architecture Base






![image3.png](word_fromPDF_v6_images/image3.png)


## Project Infrastructure Foundation

![image4.jpeg](word_fromPDF_v6_images/image4.jpeg)



ORG.


![image5.png](word_fromPDF_v6_images/image5.png)MANAGEMENT ACCOUNT


IAM





SCP





OrganizationAccountAccessRole

SCP


Permission Sets


PROD UNIT















SCP

Data Account

Client Account

Security Account










![image7.jpeg](word_fromPDF_v6_images/image7.jpeg)![image8.jpeg](word_fromPDF_v6_images/image8.jpeg)ROOT UNIT

DEV UNIT

TEAM



![image9.png](word_fromPDF_v6_images/image9.png)




![image10.png](word_fromPDF_v6_images/image10.png)![image12.jpeg](word_fromPDF_v6_images/image12.jpeg)Admin AccountAdmin Account:Sandbox Environment:Production Environment

: Identity Center

: Budget

*SCP = Service Control Policy


## Project Infrastructure Foundation

![image4.jpeg](word_fromPDF_v6_images/image4.jpeg)



ORG.


MANAGEMENT ACCOUNT

Budget Alert



![image5.png](word_fromPDF_v6_images/image5.png)


Data AccountData AccountSCP

Billing








SCP

Client Account

Security Account



Admin AccountAdmin AccountPermission Sets


PROD UNIT















SCP

Data Account

Client Account

Security Account










![image7.jpeg](word_fromPDF_v6_images/image7.jpeg)![image8.jpeg](word_fromPDF_v6_images/image8.jpeg)ROOT UNIT

DEV UNIT

TEAM



![image9.png](word_fromPDF_v6_images/image9.png)




![image10.png](word_fromPDF_v6_images/image10.png)![image12.jpeg](word_fromPDF_v6_images/image12.jpeg)Admin AccountAdmin Account:Sandbox Environment:Production Environment

: Identity Center

: Budget

*SCP = Service Control Policy


Identity Federation and Permissions









![image12.jpeg](word_fromPDF_v6_images/image12.jpeg)Permission Sets










![image17.png](word_fromPDF_v6_images/image17.png)![image16.png](word_fromPDF_v6_images/image16.png)



























![image7.jpeg](word_fromPDF_v6_images/image7.jpeg)![image5.png](word_fromPDF_v6_images/image5.png)![image29.png](word_fromPDF_v6_images/image29.png)![image28.png](word_fromPDF_v6_images/image28.png)Service Control Policy

Permission Set: Resource Policy granting access


# ![image2.png](word_fromPDF_v6_images/image2.png)Request Flow Overview
















![image30.png](word_fromPDF_v6_images/image30.png)




Domain Records

Mngmnt. Account












Gets redirected back to webpage, now retrieving his info.



Client Account

Certificate Manager



Data Account




Admin Account






![image17.png](word_fromPDF_v6_images/image17.png)client.example.com

admin.example.com







### ![image16.png](word_fromPDF_v6_images/image16.png)Jack

CDN

Source Code

DynamoDB

### Admin





![image31.png](word_fromPDF_v6_images/image31.png)API




Lambda

PK=id 2a 1j

…

Name Andy Jack

Age 18

16

Grade…

F…

A+…


PK=cstSK

Name

Age


PERSON Andy#2aAndy18}

PERSONJack#1jJack16

…

![image31.png](word_fromPDF_v6_images/image31.png)Security Account








Gets redirected to login UI to authenticate and get JWT back




auth.example.com


![image34.png](word_fromPDF_v6_images/image34.png)


![image7.jpeg](word_fromPDF_v6_images/image7.jpeg): Authentication: Retrieve/Update: One Time Operation / Static Configuration


![image45.png](word_fromPDF_v6_images/image45.png)Request Flow Overview: Client-Side





![image34.png](word_fromPDF_v6_images/image34.png)Domain Records

Mngmnt. Account








Certificate Manager



Client Account

Data Account








![image17.png](word_fromPDF_v6_images/image17.png)![image52.png](word_fromPDF_v6_images/image52.png)client.example.com



OAC



SSE*



AWS

Owned




### Jack

CDNSource Code

Bucket Policy




PK=id

Name

Age

Grade


1jJack16A+1jJack16A+2a0d236  6f4922e1dw




API

1jbc535

…

67f1f5

13fe2



CSE*CSE*Customer Managed




Security Account





![image22.png](word_fromPDF_v6_images/image22.png)![image7.jpeg](word_fromPDF_v6_images/image7.jpeg)auth.example.com








:Public:Private

: Authentication

: Retrieve/Update: One Time Operation / Static Configuration

= DDB Endpoint


![image54.png](word_fromPDF_v6_images/image54.png)Request Flow Overview: Admin-Side








There are 3 roles at play here. The role in Admin App Acc.: it allows both lambda functions to assume either role in Data Acc., return info to api that invoked it.


One role in Data Acc. is granted access to DDB base table for retrieval. It is allowed KMS operations. Logically, it is also granted access by key policy to use key to perform CSE.

This role is the same used by Lambda from Client Acc..


Second role in Data Acc. is only granted access to DDB summary table to retrieve summary info on clients. Both roles trust the role in Admin Account.





![image52.png](word_fromPDF_v6_images/image52.png)Domain Records

Mngmnt. Account
















AWS

Owned




SSE*

Certificate Manager

Data Account






OAC



Admin Account



![image16.png](word_fromPDF_v6_images/image16.png)admin.example.com







PK=id 2a 1j

…



Name 0d236

bc535



Age 6f4922

67f1f5



Grade e1dw 13fe2

Bucket Policy



“13fe2”

Source Code



“A”

CDN




API

### Admin



![image50.png](word_fromPDF_v6_images/image50.png)Customer Managed

CSE**

PK=cstSKNameAgePERSONAndy#2aAndy18PERSONJack#1jJack16PK=cstSKNameAgePERSONAndy#2aAndy18PERSONJack#1jJack16*

}





Security Account





![image7.jpeg](word_fromPDF_v6_images/image7.jpeg)auth.example.com








![image40.png](word_fromPDF_v6_images/image40.png)![image22.png](word_fromPDF_v6_images/image22.png)= DDB Endpoint

: Authentication

: Retrieve/Update: One Time Operation / Static Configuration

:Public:Private


# Logging & Monitoring











![image56.jpeg](word_fromPDF_v6_images/image56.jpeg)All API calls are logged in every account by CloudTrail. The logs are then written to a central bucket located in the Security Acc.: this is an Organization Trail. Log File Integrity is turned on to make sure log files are tampered.


We’re also making sure that any unsuccessful attempt to do something, due to a lack of permission, notifies the admins. This makes sure that we have time to stop a privilege escalation for instance.


EventBridge pulls these access denied/ unauthorized operation errors from internal streams. They are sent directly to the default event Bus in each account which forwards it to Bus in Sec. Acc..

Admin is notified by SNS topic set as target to the Bus rule.

All services are subject to failures. We need to make sure to remediate in a timely manner to these failures to keep our site/ business running smoothly.


Metrics and/or logs are sent directly from services to CloudWatch.

An alarm is triggered if the threshold defined is exceeded in the case of metrics being directly sent. When it comes to logs, we define a metric filter and the output of logs —> metric filter is metrics. An alarm is triggered if the threshold defined for the metrics is exceeded. In both cases, the Admin is notified via an SNS topic integrated with the alarm.


It is important to note that the logs are not coming from CloudTrail. Indeed, CloudTrail cannot monitor a Lambda function failing to execute for example. CloudTrail records API activities and not service behavior.


![image48.jpeg](word_fromPDF_v6_images/image48.jpeg)Organization-Wide Logging & Access Denied/Unauthorized Operation Alerts


Client AccountClient AccountData AccountData AccountAdmin AccountAdmin Account




APIGWAPIGWLambdaLambdaKMSKMSDynamoDBDynamoDBAPIGWAPIGWLambdaLambda
































Cognito

Security Account


























![image26.jpeg](word_fromPDF_v6_images/image26.jpeg)![image62.jpeg](word_fromPDF_v6_images/image62.jpeg)![image63.jpeg](word_fromPDF_v6_images/image63.jpeg)![image61.jpeg](word_fromPDF_v6_images/image61.jpeg)![image7.jpeg](word_fromPDF_v6_images/image7.jpeg): Organization Trail

: Monitoring through EventBridge

: Log files Bucket: CloudTrail: EventBridge: SNS Topic


Security. AccountSecurity. AccountAdmin AccountAdmin AccountService Level Alerts





![image41.png](word_fromPDF_v6_images/image41.png)CognitoCognitoLambdaLambdaAPIGWAPIGWMngmnt. Account

Client Account

Data Account






Route53

APIGWLambda

KMSDynamoDB
















































![image65.jpeg](word_fromPDF_v6_images/image65.jpeg)![image61.jpeg](word_fromPDF_v6_images/image61.jpeg)![image7.jpeg](word_fromPDF_v6_images/image7.jpeg): Service Operations Logs

: Alarm triggered/Admin notified

: CloudWatch: SNS Topic


# Threat Detection




![image66.png](word_fromPDF_v6_images/image66.png)GuardDuty when enabled in the account starts automatically pulling logs from VPC Flow logs, Route 53 resolver query logging and CloudTrail management events internal streams. There is no need to turn them on manually.


After being enabled, the service is going to start analyzing the logs as a whole, and use machine learning to detect threats as they occur.

These threats are referred to as findings. The service is integrated with SNS to notify the admin.


It is to note that GuardDuty, in the first 2 weeks is not going to be generating findings, because it is still unfamiliar with normal behavior in the account.


# Threat Detection





![image41.png](word_fromPDF_v6_images/image41.png)Mngmnt. Account

Client Account

Security. Account

Admin Account

Data Account






Route53

VPCCloudTrail

Route53VPCCloudTrail

Route53VPCCloudTrail

Route53VPCCloudTrail

Route53VPCCloudTrail






















Finding: Policy:S3/BucketAnonymousAccessGranted

![image69.png](word_fromPDF_v6_images/image69.png)![image70.png](word_fromPDF_v6_images/image70.png)![image71.png](word_fromPDF_v6_images/image71.png)![image7.jpeg](word_fromPDF_v6_images/image7.jpeg)Alert is done through integratíon with SNS








: Logs streamed internally

: GuardDuty collecting from internal streams of logs

: VPC Flow Logs: Route53 Resolver Query Logging: CloudTrail Management Events


Infrastructure as Code










![image73.png](word_fromPDF_v6_images/image73.png)


![image16.png](word_fromPDF_v6_images/image16.png)![image12.jpeg](word_fromPDF_v6_images/image12.jpeg)![image83.png](word_fromPDF_v6_images/image83.png)![image31.png](word_fromPDF_v6_images/image31.png)


![image84.png](word_fromPDF_v6_images/image84.png)






















![image77.png](word_fromPDF_v6_images/image77.png)![image74.png](word_fromPDF_v6_images/image74.png)![image83.png](word_fromPDF_v6_images/image83.png)![image7.jpeg](word_fromPDF_v6_images/image7.jpeg): Terraform: GitHub: GitHub Actions
