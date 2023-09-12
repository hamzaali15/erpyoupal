import frappe
import base64
import json
import requests
from requests.structures import CaseInsensitiveDict
from frappe.utils import get_site_name, getdate, now

def get_account_credentials():
	result = {
		"Sovren-AccountId": "42899245",
		"Sovren-ServiceKey": "fuMEQ59pEtnKJr0cuc5O/ZZaAursegVhcqZmnXpD"
	}
	return result

def resume_parser(unparsed_resume_base64):
	result = {
		"info": {},
		"resume_data": {},
		"contact_information": {},
		"personal_attributes": {},
		"education": {},
		"employment_history": {},
		"skills_data": [],
		"skills": {},
		"certifications": [],
		"licenses": [],
		"associations": [],
		"language_competencies": [],
		"military_experience": [],
		"security_credentials": [],
		"references": [],
		"achievements": [],
		"training": {},
		"resume_metadata": {},
		"user_defined_tags": []
	}

	account_credentials = get_account_credentials()
	if account_credentials:
		#Set url
		url = "https://eu-rest.resumeparsing.com/v10/parser/resume"

		#Set headers
		headers = CaseInsensitiveDict()
		headers["Content-Type"] = "application/json"
		headers["Accept"] = "application/json"
		headers["Sovren-AccountId"] = account_credentials["Sovren-AccountId"]
		headers["Sovren-ServiceKey"] = account_credentials["Sovren-ServiceKey"]

		#Set data
		data_dict = {
			"DocumentAsBase64String": unparsed_resume_base64,
			"DocumentLastModified": str(getdate(now())),
			"GeocodeOptions": {
				"IncludeGeocoding": True
			},
			"OutputHtml": True,
			"HideHtmlImages": True,
			"OutputRtf": True,
			"OutputCandidateImage": True,
			"OutputPdf": True,
			"ProfessionsSettings": {
				"Normalize": True
			},
			"SkillsSettings": {
				"Normalize": True
			}
		}
		data = json.dumps(data_dict)

		#Run post request
		request_response = requests.post(url, headers=headers, data=data)
		request_response_json = request_response.json()
		if request_response_json:
			result["info"] = str(request_response_json.get("Info"))
			if request_response_json.get("Value"):
				result["resume_data"] = dict(request_response_json["Value"]["ResumeData"])
				
				if "ContactInformation" in result["resume_data"]:
					result["contact_information"] = dict(result["resume_data"]["ContactInformation"])
					result["resume_data"].pop("ContactInformation")

				if "PersonalAttributes" in result["resume_data"]:
					result["personal_attributes"] = dict(result["resume_data"]["PersonalAttributes"])
					result["resume_data"].pop("PersonalAttributes")

				if "Education" in result["resume_data"]:
					result["education"] = dict(result["resume_data"]["Education"])
					result["resume_data"].pop("Education")

				if "EmploymentHistory" in result["resume_data"]:
					result["employment_history"] = dict(result["resume_data"]["EmploymentHistory"])
					result["resume_data"].pop("EmploymentHistory")

				if "SkillsData" in result["resume_data"]:
					result["skills_data"] = result["resume_data"]["SkillsData"]
					result["resume_data"].pop("SkillsData")

				if "Skills" in result["resume_data"]:
					result["skills"] = dict(result["resume_data"]["Skills"])
					result["resume_data"].pop("Skills")

				if "Certifications" in result["resume_data"]:
					result["certifications"] = result["resume_data"]["Certifications"]
					result["resume_data"].pop("Certifications")

				if "Licenses" in result["resume_data"]:
					result["licenses"] = result["resume_data"]["Licenses"]
					result["resume_data"].pop("Licenses")

				if "Associations" in result["resume_data"]:
					result["associations"] = result["resume_data"]["Associations"]
					result["resume_data"].pop("Associations")

				if "LanguageCompetencies" in result["resume_data"]:
					result["language_competencies"] = result["resume_data"]["LanguageCompetencies"]
					result["resume_data"].pop("LanguageCompetencies")

				if "MilitaryExperience" in result["resume_data"]:
					result["military_experience"] = result["resume_data"]["MilitaryExperience"]
					result["resume_data"].pop("MilitaryExperience")

				if "SecurityCredentials" in result["resume_data"]:
					result["security_credentials"] = result["resume_data"]["SecurityCredentials"]
					result["resume_data"].pop("SecurityCredentials")

				if "References" in result["resume_data"]:
					result["references"] = result["resume_data"]["References"]
					result["resume_data"].pop("References")

				if "Achievements" in result["resume_data"]:
					result["achievements"] = result["resume_data"]["Achievements"]
					result["resume_data"].pop("Achievements")

				if "Training" in result["resume_data"]:
					result["training"] = dict(result["resume_data"]["Training"])
					result["resume_data"].pop("Training")

				if "ResumeMetadata" in result["resume_data"]:
					result["resume_metadata"] = dict(result["resume_data"]["ResumeMetadata"])
					result["resume_data"].pop("ResumeMetadata")

				if "UserDefinedTags" in result["resume_data"]:
					result["user_defined_tags"] = result["resume_data"]["UserDefinedTags"]
					result["resume_data"].pop("UserDefinedTags")

	return result



#DATA
#{
#  "DocumentAsBase64String": "string",
#  "DocumentLastModified": "string",
#  "GeocodeOptions": {
#    "IncludeGeocoding": True,
#    "Provider": "string",
#    "ProviderKey": "string",
#    "PostalAddress": {
#      "CountryCode": "string",
#      "PostalCode": "string",
#      "Region": "string",
#      "Municipality": "string",
#      "AddressLine": "string"
#    },
#    "GeoCoordinates": {
#      "Latitude": 0,
#      "Longitude": 0
#    }
#  },
#  "IndexingOptions": {
#    "IndexId": "string",
#    "DocumentId": "string",
#    "UserDefinedTags": [
#      "string"
#    ]
#  },
#  "OutputHtml": True,
#  "HideHtmlImages": True,
#  "OutputRtf": True,
#  "OutputCandidateImage": True,
#  "OutputPdf": True,
#  "Configuration": "string",
#  "SkillsData": [
#    "string"
#  ],
#  "NormalizerData": "string",
#  "ProfessionsSettings": {
#    "Normalize": True
#  },
#  "SkillsSettings": {
#    "Normalize": True,
#    "TaxonomyVersion": "string"
#  }
#}



#RESPONSE
#{
#  "Info": {
#    "Code": "Success",
#    "Message": "string",
#    "TransactionId": "string",
#    "EngineVersion": "string",
#    "ApiVersion": "string",
#    "TotalElapsedMilliseconds": 0,
#    "TransactionCost": 0,
#    "CustomerDetails": {
#      "AccountId": "string",
#      "Name": "string",
#      "IPAddress": "string",
#      "Region": "string",
#      "CreditsRemaining": 0,
#      "CreditsUsed": 0,
#      "ExpirationDate": "2022-09-26",
#      "MaximumConcurrentRequests": 0
#    }
#  },
#  "Value": {
#    "ParsingResponse": {
#      "Code": "Success",
#      "Message": "string"
#    },
#    "GeocodeResponse": {
#      "Code": "Success",
#      "Message": "string"
#    },
#    "IndexingResponse": {
#      "Code": "Success",
#      "Message": "string"
#    },
#    "ResumeData": {
#      "ContactInformation": {
#        "CandidateName": {
#          "FormattedName": "string",
#          "Prefix": "string",
#          "GivenName": "string",
#          "Moniker": "string",
#          "MiddleName": "string",
#          "FamilyName": "string",
#          "Suffix": "string"
#        },
#        "Telephones": [
#          {
#            "Raw": "string",
#            "Normalized": "string",
#            "InternationalCountryCode": "string",
#            "AreaCityCode": "string",
#            "SubscriberNumber": "string"
#          }
#        ],
#        "EmailAddresses": [
#          "string"
#        ],
#        "Location": {
#          "CountryCode": "string",
#          "PostalCode": "string",
#          "Regions": [
#            "string"
#          ],
#          "Municipality": "string",
#          "StreetAddressLines": [
#            "string"
#          ],
#          "GeoCoordinates": {
#            "Latitude": 0,
#            "Longitude": 0,
#            "Source": "string"
#          }
#        },
#        "WebAddresses": [
#          {
#            "Address": "string",
#            "Type": "string"
#          }
#        ]
#      },
#      "ProfessionalSummary": "string",
#      "Objective": "string",
#      "CoverLetter": "string",
#      "PersonalAttributes": {
#        "Availability": "string",
#        "Birthplace": "string",
#        "CurrentLocation": "string",
#        "CurrentSalary": {
#          "Currency": "string",
#          "Amount": 0
#        },
#        "DateOfBirth": {
#          "Date": "2022-09-26",
#          "IsCurrentDate": true,
#          "FoundYear": true,
#          "FoundMonth": true,
#          "FoundDay": true
#        },
#        "DrivingLicense": "string",
#        "FamilyComposition": "string",
#        "FathersName": "string",
#        "Gender": "string",
#        "HukouCity": "string",
#        "HukouArea": "string",
#        "MaritalStatus": "string",
#        "MothersMaidenName": "string",
#        "MotherTongue": "string",
#        "NationalIdentities": [
#          {
#            "Number": "string",
#            "Phrase": "string"
#          }
#        ],
#        "Nationality": "string",
#        "PassportNumber": "string",
#        "PreferredLocation": "string",
#        "RequiredSalary": {
#          "Currency": "string",
#          "Amount": 0
#        },
#        "VisaStatus": "string",
#        "WillingToRelocate": "string"
#      },
#      "Education": {
#        "HighestDegree": {
#          "Name": {
#            "Raw": "string",
#            "Normalized": "string"
#          },
#          "Type": "string"
#        },
#        "EducationDetails": [
#          {
#            "Id": "string",
#            "Text": "string",
#            "SchoolName": {
#              "Raw": "string",
#              "Normalized": "string"
#            },
#            "SchoolType": "string",
#            "Location": {
#              "CountryCode": "string",
#              "PostalCode": "string",
#              "Regions": [
#                "string"
#              ],
#              "Municipality": "string",
#              "StreetAddressLines": [
#                "string"
#              ],
#              "GeoCoordinates": {
#                "Latitude": 0,
#                "Longitude": 0,
#                "Source": "string"
#              }
#            },
#            "Degree": {
#              "Name": {
#                "Raw": "string",
#                "Normalized": "string"
#              },
#              "Type": "string"
#            },
#            "Majors": [
#              "string"
#            ],
#            "Minors": [
#              "string"
#            ],
#            "GPA": {
#              "Score": "string",
#              "ScoringSystem": "string",
#              "MaxScore": "string",
#              "MinimumScore": "string",
#              "NormalizedScore": 0
#            },
#            "LastEducationDate": {
#              "Date": "2022-09-26",
#              "IsCurrentDate": true,
#              "FoundYear": true,
#              "FoundMonth": true,
#              "FoundDay": true
#            },
#            "Graduated": {
#              "Value": true
#            }
#          }
#        ]
#      },
#      "EmploymentHistory": {
#        "ExperienceSummary": {
#          "Description": "string",
#          "MonthsOfWorkExperience": 0,
#          "MonthsOfManagementExperience": 0,
#          "ExecutiveType": "string",
#          "AverageMonthsPerEmployer": 0,
#          "FulltimeDirectHirePredictiveIndex": 0,
#          "ManagementStory": "string",
#          "CurrentManagementLevel": "string",
#          "ManagementScore": 0,
#          "AttentionNeeded": "string"
#        },
#        "Positions": [
#          {
#            "Id": "string",
#            "Employer": {
#              "Name": {
#                "Probability": "string",
#                "Raw": "string",
#                "Normalized": "string"
#              },
#              "OtherFoundName": {
#                "Raw": "string",
#                "Normalized": "string"
#              },
#              "Location": {
#                "CountryCode": "string",
#                "PostalCode": "string",
#                "Regions": [
#                  "string"
#                ],
#                "Municipality": "string",
#                "StreetAddressLines": [
#                  "string"
#                ],
#                "GeoCoordinates": {
#                  "Latitude": 0,
#                  "Longitude": 0,
#                  "Source": "string"
#                }
#              }
#            },
#            "RelatedToByDates": [
#              "string"
#            ],
#            "RelatedToByCompanyName": [
#              "string"
#            ],
#            "IsSelfEmployed": true,
#            "IsCurrent": true,
#            "JobTitle": {
#              "Raw": "string",
#              "Normalized": "string",
#              "Probability": "string",
#              "Variations": [
#                "string"
#              ]
#            },
#            "StartDate": {
#              "Date": "2022-09-26",
#              "IsCurrentDate": true,
#              "FoundYear": true,
#              "FoundMonth": true,
#              "FoundDay": true
#            },
#            "EndDate": {
#              "Date": "2022-09-26",
#              "IsCurrentDate": true,
#              "FoundYear": true,
#              "FoundMonth": true,
#              "FoundDay": true
#            },
#            "NumberEmployeesSupervised": {
#              "Value": 0
#            },
#            "JobType": "string",
#            "TaxonomyName": "string",
#            "SubTaxonomyName": "string",
#            "JobLevel": "string",
#            "TaxonomyPercentage": 0,
#            "Description": "string",
#            "Bullets": [
#              {
#                "Type": "string",
#                "Text": "string"
#              }
#            ],
#            "NormalizedProfession": {
#              "Profession": {
#                "CodeId": 0,
#                "Description": "string"
#              },
#              "Group": {
#                "CodeId": 0,
#                "Description": "string"
#              },
#              "Class": {
#                "CodeId": 0,
#                "Description": "string"
#              },
#              "ISCO": {
#                "Version": "string",
#                "CodeId": 0,
#                "Description": "string"
#              },
#              "ONET": {
#                "Version": "string",
#                "CodeId": "string",
#                "Description": "string"
#              },
#              "Confidence": 0
#            }
#          }
#        ]
#      },
#      "SkillsData": [
#        {
#          "Root": "string",
#          "Taxonomies": [
#            {
#              "Id": "string",
#              "Name": "string",
#              "PercentOfOverall": 0,
#              "SubTaxonomies": [
#                {
#                  "SubTaxonomyId": "string",
#                  "SubTaxonomyName": "string",
#                  "PercentOfOverall": 0,
#                  "PercentOfParent": 0,
#                  "Skills": [
#                    {
#                      "Id": "string",
#                      "Name": "string",
#                      "FoundIn": [
#                        {
#                          "SectionType": "string",
#                          "Id": "string"
#                        }
#                      ],
#                      "ExistsInText": true,
#                      "Type": "string",
#                      "Variations": [
#                        {
#                          "Id": "string",
#                          "Name": "string",
#                          "FoundIn": [
#                            {
#                              "SectionType": "string",
#                              "Id": "string"
#                            }
#                          ],
#                          "ExistsInText": true,
#                          "MonthsExperience": {
#                            "Value": 0
#                          },
#                          "LastUsed": {
#                            "Value": "2022-09-26"
#                          }
#                        }
#                      ],
#                      "MonthsExperience": {
#                        "Value": 0
#                      },
#                      "LastUsed": {
#                        "Value": "2022-09-26"
#                      },
#                      "ChildrenMonthsExperience": {
#                        "Value": 0
#                      },
#                      "ChildrenLastUsed": {
#                        "Value": "2022-09-26"
#                      }
#                    }
#                  ]
#                }
#              ]
#            }
#          ]
#        }
#      ],
#      "Skills": {
#        "Raw": [
#          {
#            "Name": "string",
#            "FoundIn": [
#              {
#                "SectionType": "string",
#                "Id": "string"
#              }
#            ],
#            "MonthsExperience": {
#              "Value": 0
#            },
#            "LastUsed": {
#              "Value": "2022-09-26"
#            }
#          }
#        ],
#        "Normalized": [
#          {
#            "Name": "string",
#            "Id": "string",
#            "Type": "string",
#            "FoundIn": [
#              {
#                "SectionType": "string",
#                "Id": "string"
#              }
#            ],
#            "MonthsExperience": {
#              "Value": 0
#            },
#            "LastUsed": {
#              "Value": "2022-09-26"
#            },
#            "RawSkills": [
#              "string"
#            ]
#          }
#        ],
#        "RelatedProfessionClasses": [
#          {
#            "Name": "string",
#            "Id": "string",
#            "Percent": 0,
#            "Groups": [
#              {
#                "Name": "string",
#                "Id": "string",
#                "Percent": 0,
#                "NormalizedSkills": [
#                  "string"
#                ]
#              }
#            ]
#          }
#        ]
#      },
#      "Certifications": [
#        {
#          "Name": "string",
#          "MatchedFromList": true,
#          "IsVariation": true
#        }
#      ],
#      "Licenses": [
#        {
#          "Name": "string",
#          "MatchedFromList": true
#        }
#      ],
#      "Associations": [
#        {
#          "Organization": "string",
#          "Role": "string",
#          "FoundInContext": "string"
#        }
#      ],
#      "LanguageCompetencies": [
#        {
#          "Language": "string",
#          "LanguageCode": "string",
#          "FoundInContext": "string"
#        }
#      ],
#      "MilitaryExperience": [
#        {
#          "Country": "string",
#          "Service": {
#            "Name": "string",
#            "Branch": "string",
#            "Rank": "string"
#          },
#          "StartDate": {
#            "Date": "2022-09-26",
#            "IsCurrentDate": true,
#            "FoundYear": true,
#            "FoundMonth": true,
#            "FoundDay": true
#          },
#          "EndDate": {
#            "Date": "2022-09-26",
#            "IsCurrentDate": true,
#            "FoundYear": true,
#            "FoundMonth": true,
#            "FoundDay": true
#          },
#          "FoundInContext": "string"
#        }
#      ],
#      "SecurityCredentials": [
#        {
#          "Name": "string",
#          "FoundInContext": "string"
#        }
#      ],
#      "References": [
#        {
#          "ReferenceName": {
#            "FormattedName": "string",
#            "Prefix": "string",
#            "GivenName": "string",
#            "Moniker": "string",
#            "MiddleName": "string",
#            "FamilyName": "string",
#            "Suffix": "string"
#          },
#          "Title": "string",
#          "Company": "string",
#          "Type": "string",
#          "Location": {
#            "CountryCode": "string",
#            "PostalCode": "string",
#            "Regions": [
#              "string"
#            ],
#            "Municipality": "string",
#            "StreetAddressLines": [
#              "string"
#            ],
#            "GeoCoordinates": {
#              "Latitude": 0,
#              "Longitude": 0,
#              "Source": "string"
#            }
#          },
#          "Telephones": [
#            {
#              "Raw": "string",
#              "Normalized": "string"
#            }
#          ],
#          "EmailAddresses": [
#            "string"
#          ],
#          "WebAddresses": [
#            {
#              "Address": "string",
#              "Type": "string"
#            }
#          ]
#        }
#      ],
#      "Achievements": [
#        "string"
#      ],
#      "Training": {
#        "Text": "string",
#        "Trainings": [
#          {
#            "Text": "string",
#            "Entity": "string",
#            "Qualifications": [
#              "string"
#            ],
#            "StartDate": {
#              "Date": "2022-09-26",
#              "IsCurrentDate": true,
#              "FoundYear": true,
#              "FoundMonth": true,
#              "FoundDay": true
#            },
#            "EndDate": {
#              "Date": "2022-09-26",
#              "IsCurrentDate": true,
#              "FoundYear": true,
#              "FoundMonth": true,
#              "FoundDay": true
#            }
#          }
#        ]
#      },
#      "QualificationsSummary": "string",
#      "Hobbies": "string",
#      "Patents": "string",
#      "Publications": "string",
#      "SpeakingEngagements": "string",
#      "ResumeMetadata": {
#        "FoundSections": [
#          {
#            "FirstLineNumber": 0,
#            "LastLineNumber": 0,
#            "SectionType": "string",
#            "HeaderTextFound": "string"
#          }
#        ],
#        "ResumeQuality": [
#          {
#            "Level": "string",
#            "Findings": [
#              {
#                "QualityCode": "string",
#                "SectionIdentifiers": [
#                  {
#                    "SectionType": "string",
#                    "Id": "string"
#                  }
#                ],
#                "Message": "string"
#              }
#            ]
#          }
#        ],
#        "ReservedData": {
#          "Phones": [
#            "string"
#          ],
#          "Names": [
#            "string"
#          ],
#          "EmailAddresses": [
#            "string"
#          ],
#          "Urls": [
#            "string"
#          ],
#          "OtherData": [
#            "string"
#          ]
#        },
#        "PlainText": "string",
#        "DocumentLanguage": "string",
#        "DocumentCulture": "string",
#        "ParserSettings": "string",
#        "DocumentLastModified": "2022-09-26",
#        "SovrenSignature": [
#          "string"
#        ]
#      },
#      "UserDefinedTags": [
#        "string"
#      ]
#    },
#    "RedactedResumeData": {
#      "ContactInformation": {
#        "CandidateName": {
#          "FormattedName": "string",
#          "Prefix": "string",
#          "GivenName": "string",
#          "Moniker": "string",
#          "MiddleName": "string",
#          "FamilyName": "string",
#          "Suffix": "string"
#        },
#        "Telephones": [
#          {
#            "Raw": "string",
#            "Normalized": "string",
#            "InternationalCountryCode": "string",
#            "AreaCityCode": "string",
#            "SubscriberNumber": "string"
#          }
#        ],
#        "EmailAddresses": [
#          "string"
#        ],
#        "Location": {
#          "CountryCode": "string",
#          "PostalCode": "string",
#          "Regions": [
#            "string"
#          ],
#          "Municipality": "string",
#          "StreetAddressLines": [
#            "string"
#          ],
#          "GeoCoordinates": {
#            "Latitude": 0,
#            "Longitude": 0,
#            "Source": "string"
#          }
#        },
#        "WebAddresses": [
#          {
#            "Address": "string",
#            "Type": "string"
#          }
#        ]
#      },
#      "ProfessionalSummary": "string",
#      "Objective": "string",
#      "CoverLetter": "string",
#      "PersonalAttributes": {
#        "Availability": "string",
#        "Birthplace": "string",
#        "CurrentLocation": "string",
#        "CurrentSalary": {
#          "Currency": "string",
#          "Amount": 0
#        },
#        "DateOfBirth": {
#          "Date": "2022-09-26",
#          "IsCurrentDate": true,
#          "FoundYear": true,
#          "FoundMonth": true,
#          "FoundDay": true
#        },
#        "DrivingLicense": "string",
#        "FamilyComposition": "string",
#        "FathersName": "string",
#        "Gender": "string",
#        "HukouCity": "string",
#        "HukouArea": "string",
#        "MaritalStatus": "string",
#        "MothersMaidenName": "string",
#        "MotherTongue": "string",
#        "NationalIdentities": [
#          {
#            "Number": "string",
#            "Phrase": "string"
#          }
#        ],
#        "Nationality": "string",
#        "PassportNumber": "string",
#        "PreferredLocation": "string",
#        "RequiredSalary": {
#          "Currency": "string",
#          "Amount": 0
#        },
#        "VisaStatus": "string",
#        "WillingToRelocate": "string"
#      },
#      "Education": {
#        "HighestDegree": {
#          "Name": {
#            "Raw": "string",
#            "Normalized": "string"
#          },
#          "Type": "string"
#        },
#        "EducationDetails": [
#          {
#            "Id": "string",
#            "Text": "string",
#            "SchoolName": {
#              "Raw": "string",
#              "Normalized": "string"
#            },
#            "SchoolType": "string",
#            "Location": {
#              "CountryCode": "string",
#              "PostalCode": "string",
#              "Regions": [
#                "string"
#              ],
#              "Municipality": "string",
#              "StreetAddressLines": [
#                "string"
#              ],
#              "GeoCoordinates": {
#                "Latitude": 0,
#                "Longitude": 0,
#                "Source": "string"
#              }
#            },
#            "Degree": {
#              "Name": {
#                "Raw": "string",
#                "Normalized": "string"
#              },
#              "Type": "string"
#            },
#            "Majors": [
#              "string"
#            ],
#            "Minors": [
#              "string"
#            ],
#            "GPA": {
#              "Score": "string",
#              "ScoringSystem": "string",
#              "MaxScore": "string",
#              "MinimumScore": "string",
#              "NormalizedScore": 0
#            },
#            "LastEducationDate": {
#              "Date": "2022-09-26",
#              "IsCurrentDate": true,
#              "FoundYear": true,
#              "FoundMonth": true,
#              "FoundDay": true
#            },
#            "Graduated": {
#              "Value": true
#            }
#          }
#        ]
#      },
#      "EmploymentHistory": {
#        "ExperienceSummary": {
#          "Description": "string",
#          "MonthsOfWorkExperience": 0,
#          "MonthsOfManagementExperience": 0,
#          "ExecutiveType": "string",
#          "AverageMonthsPerEmployer": 0,
#          "FulltimeDirectHirePredictiveIndex": 0,
#          "ManagementStory": "string",
#          "CurrentManagementLevel": "string",
#          "ManagementScore": 0,
#          "AttentionNeeded": "string"
#        },
#        "Positions": [
#          {
#            "Id": "string",
#            "Employer": {
#              "Name": {
#                "Probability": "string",
#                "Raw": "string",
#                "Normalized": "string"
#              },
#              "OtherFoundName": {
#                "Raw": "string",
#                "Normalized": "string"
#              },
#              "Location": {
#                "CountryCode": "string",
#                "PostalCode": "string",
#                "Regions": [
#                  "string"
#                ],
#                "Municipality": "string",
#                "StreetAddressLines": [
#                  "string"
#                ],
#                "GeoCoordinates": {
#                  "Latitude": 0,
#                  "Longitude": 0,
#                  "Source": "string"
#                }
#              }
#            },
#            "RelatedToByDates": [
#              "string"
#            ],
#            "RelatedToByCompanyName": [
#              "string"
#            ],
#            "IsSelfEmployed": true,
#            "IsCurrent": true,
#            "JobTitle": {
#              "Raw": "string",
#              "Normalized": "string",
#              "Probability": "string",
#              "Variations": [
#                "string"
#              ]
#            },
#            "StartDate": {
#              "Date": "2022-09-26",
#              "IsCurrentDate": true,
#              "FoundYear": true,
#              "FoundMonth": true,
#              "FoundDay": true
#            },
#            "EndDate": {
#              "Date": "2022-09-26",
#              "IsCurrentDate": true,
#              "FoundYear": true,
#              "FoundMonth": true,
#              "FoundDay": true
#            },
#            "NumberEmployeesSupervised": {
#              "Value": 0
#            },
#            "JobType": "string",
#            "TaxonomyName": "string",
#            "SubTaxonomyName": "string",
#            "JobLevel": "string",
#            "TaxonomyPercentage": 0,
#            "Description": "string",
#            "Bullets": [
#              {
#                "Type": "string",
#                "Text": "string"
#              }
#            ],
#            "NormalizedProfession": {
#              "Profession": {
#                "CodeId": 0,
#                "Description": "string"
#              },
#              "Group": {
#                "CodeId": 0,
#                "Description": "string"
#              },
#              "Class": {
#                "CodeId": 0,
#                "Description": "string"
#              },
#              "ISCO": {
#                "Version": "string",
#                "CodeId": 0,
#                "Description": "string"
#              },
#              "ONET": {
#                "Version": "string",
#                "CodeId": "string",
#                "Description": "string"
#              },
#              "Confidence": 0
#            }
#          }
#        ]
#      },
#      "SkillsData": [
#        {
#          "Root": "string",
#          "Taxonomies": [
#            {
#              "Id": "string",
#              "Name": "string",
#              "PercentOfOverall": 0,
#              "SubTaxonomies": [
#                {
#                  "SubTaxonomyId": "string",
#                  "SubTaxonomyName": "string",
#                  "PercentOfOverall": 0,
#                  "PercentOfParent": 0,
#                  "Skills": [
#                    {
#                      "Id": "string",
#                      "Name": "string",
#                      "FoundIn": [
#                        {
#                          "SectionType": "string",
#                          "Id": "string"
#                        }
#                      ],
#                      "ExistsInText": true,
#                      "Type": "string",
#                      "Variations": [
#                        {
#                          "Id": "string",
#                          "Name": "string",
#                          "FoundIn": [
#                            {
#                              "SectionType": "string",
#                              "Id": "string"
#                            }
#                          ],
#                          "ExistsInText": true,
#                          "MonthsExperience": {
#                            "Value": 0
#                          },
#                          "LastUsed": {
#                            "Value": "2022-09-26"
#                          }
#                        }
#                      ],
#                      "MonthsExperience": {
#                        "Value": 0
#                      },
#                      "LastUsed": {
#                        "Value": "2022-09-26"
#                      },
#                      "ChildrenMonthsExperience": {
#                        "Value": 0
#                      },
#                      "ChildrenLastUsed": {
#                        "Value": "2022-09-26"
#                      }
#                    }
#                  ]
#                }
#              ]
#            }
#          ]
#        }
#      ],
#      "Skills": {
#        "Raw": [
#          {
#            "Name": "string",
#            "FoundIn": [
#              {
#                "SectionType": "string",
#                "Id": "string"
#              }
#            ],
#            "MonthsExperience": {
#              "Value": 0
#            },
#            "LastUsed": {
#              "Value": "2022-09-26"
#            }
#          }
#        ],
#        "Normalized": [
#          {
#            "Name": "string",
#            "Id": "string",
#            "Type": "string",
#            "FoundIn": [
#              {
#                "SectionType": "string",
#                "Id": "string"
#              }
#            ],
#            "MonthsExperience": {
#              "Value": 0
#            },
#            "LastUsed": {
#              "Value": "2022-09-26"
#            },
#            "RawSkills": [
#              "string"
#            ]
#          }
#        ],
#        "RelatedProfessionClasses": [
#          {
#            "Name": "string",
#            "Id": "string",
#            "Percent": 0,
#            "Groups": [
#              {
#                "Name": "string",
#                "Id": "string",
#                "Percent": 0,
#                "NormalizedSkills": [
#                  "string"
#                ]
#              }
#            ]
#          }
#        ]
#      },
#      "Certifications": [
#        {
#          "Name": "string",
#          "MatchedFromList": true,
#          "IsVariation": true
#        }
#      ],
#      "Licenses": [
#        {
#          "Name": "string",
#          "MatchedFromList": true
#        }
#      ],
#      "Associations": [
#        {
#          "Organization": "string",
#          "Role": "string",
#          "FoundInContext": "string"
#        }
#      ],
#      "LanguageCompetencies": [
#        {
#          "Language": "string",
#          "LanguageCode": "string",
#          "FoundInContext": "string"
#        }
#      ],
#      "MilitaryExperience": [
#        {
#          "Country": "string",
#          "Service": {
#            "Name": "string",
#            "Branch": "string",
#            "Rank": "string"
#          },
#          "StartDate": {
#            "Date": "2022-09-26",
#            "IsCurrentDate": true,
#            "FoundYear": true,
#            "FoundMonth": true,
#            "FoundDay": true
#          },
#          "EndDate": {
#            "Date": "2022-09-26",
#            "IsCurrentDate": true,
#            "FoundYear": true,
#            "FoundMonth": true,
#            "FoundDay": true
#          },
#          "FoundInContext": "string"
#        }
#      ],
#      "SecurityCredentials": [
#        {
#          "Name": "string",
#          "FoundInContext": "string"
#        }
#      ],
#      "References": [
#        {
#          "ReferenceName": {
#            "FormattedName": "string",
#            "Prefix": "string",
#            "GivenName": "string",
#            "Moniker": "string",
#            "MiddleName": "string",
#            "FamilyName": "string",
#            "Suffix": "string"
#          },
#          "Title": "string",
#          "Company": "string",
#          "Type": "string",
#          "Location": {
#            "CountryCode": "string",
#            "PostalCode": "string",
#            "Regions": [
#              "string"
#            ],
#            "Municipality": "string",
#            "StreetAddressLines": [
#              "string"
#            ],
#            "GeoCoordinates": {
#              "Latitude": 0,
#              "Longitude": 0,
#              "Source": "string"
#            }
#          },
#          "Telephones": [
#            {
#              "Raw": "string",
#              "Normalized": "string"
#            }
#          ],
#          "EmailAddresses": [
#            "string"
#          ],
#          "WebAddresses": [
#            {
#              "Address": "string",
#              "Type": "string"
#            }
#          ]
#        }
#      ],
#      "Achievements": [
#        "string"
#      ],
#      "Training": {
#        "Text": "string",
#        "Trainings": [
#          {
#            "Text": "string",
#            "Entity": "string",
#            "Qualifications": [
#              "string"
#            ],
#            "StartDate": {
#              "Date": "2022-09-26",
#              "IsCurrentDate": true,
#              "FoundYear": true,
#              "FoundMonth": true,
#              "FoundDay": true
#            },
#            "EndDate": {
#              "Date": "2022-09-26",
#              "IsCurrentDate": true,
#              "FoundYear": true,
#              "FoundMonth": true,
#              "FoundDay": true
#            }
#          }
#        ]
#      },
#      "QualificationsSummary": "string",
#      "Hobbies": "string",
#      "Patents": "string",
#      "Publications": "string",
#      "SpeakingEngagements": "string",
#      "ResumeMetadata": {
#        "FoundSections": [
#          {
#            "FirstLineNumber": 0,
#            "LastLineNumber": 0,
#            "SectionType": "string",
#            "HeaderTextFound": "string"
#          }
#        ],
#        "ResumeQuality": [
#          {
#            "Level": "string",
#            "Findings": [
#              {
#                "QualityCode": "string",
#                "SectionIdentifiers": [
#                  {
#                    "SectionType": "string",
#                    "Id": "string"
#                  }
#                ],
#                "Message": "string"
#              }
#            ]
#          }
#        ],
#        "ReservedData": {
#          "Phones": [
#            "string"
#          ],
#          "Names": [
#            "string"
#          ],
#          "EmailAddresses": [
#            "string"
#          ],
#          "Urls": [
#            "string"
#          ],
#          "OtherData": [
#            "string"
#          ]
#        },
#        "PlainText": "string",
#        "DocumentLanguage": "string",
#        "DocumentCulture": "string",
#        "ParserSettings": "string",
#        "DocumentLastModified": "2022-09-26",
#        "SovrenSignature": [
#          "string"
#        ]
#      },
#      "UserDefinedTags": [
#        "string"
#      ]
#    },
#    "ProfessionNormalizationResponse": {
#      "Code": "Success",
#      "Message": "string"
#    },
#    "ConversionMetadata": {
#      "DetectedType": "string",
#      "SuggestedFileExtension": "string",
#      "OutputValidityCode": "string",
#      "ElapsedMilliseconds": 0,
#      "DocumentHash": "string"
#    },
#    "Conversions": {
#      "PDF": "string",
#      "HTML": "string",
#      "RTF": "string",
#      "CandidateImage": "string",
#      "CandidateImageExtension": "string"
#    },
#    "ParsingMetadata": {
#      "ElapsedMilliseconds": 0,
#      "TimedOut": true,
#      "TimedOutAtMilliseconds": {
#        "Value": 0
#      },
#      "LicenseSerialNumber": "string",
#      "Enrichment": {
#        "ProfessionNormalization": {
#          "ONETVersion": "string",
#          "ISCOVersion": "string",
#          "ProfessionTaxonomyVersion": "string"
#        },
#        "Skills": {
#          "Version": "string"
#        }
#      }
#    }
#  }
#}