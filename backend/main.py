from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

import psycopg2
import io
import json
import os
import threading, time, random, copy
from datetime import datetime, timedelta

# JSON-Template

base_template = {
  "submodels": [
    {
      "id": "https://example.com/ids/sm/6283_9092_5052_7177",
      "idShort": "Nameplate",
      "category": "CONSTANT",
      "modelType": "Submodel",
      "semanticId": {
        "keys": [
          {
            "type": "GlobalReference",
            "value": "https://www.hsu-hh.de/aut/aas/nameplate"
          }
        ],
        "type": "ExternalReference"
      },
      "description": [],
      "submodelElements": [
        {
          "value": "FH Technikum Wien",
          "idShort": "Manufacturer Name",
          "category": "PARAMETER",
          "modelType": "Property",
          "valueType": "xs:string",
          "semanticId": {
            "keys": [
              {
                "type": "ConceptDescription",
                "value": "0173-1#02-AAO677#002"
              }
            ],
            "type": "ModelReference"
          },
          "description": [
            {
              "text": "This is a master project done in FH Technikum Wien",
              "language": "en"
            },
            {
              "text": "Das ist ein Master Projekt aus dem FH Technikum Wien",
              "language": "de"
            }
          ],
          "displayName": [
            {
              "text": "FH Technikum Wien",
              "language": "en"
            },
            {
              "text": "FH Technikum Wien",
              "language": "de"
            }
          ]
        },
        {
          "idShort": "PhysicalAddress",
          "category": "PARAMETER",
          "modelType": "SubmodelElementCollection",
          "description": [
            {
              "text": "Contact and location details of FH Technikum Wien",
            "language": "en"
          },
          {
            "text": "Kontakt- und Standortdetails der FH Technikum Wien",
            "language": "de"
          }
        ],
        "value": [
          {
            "idShort": "Department",
            "modelType": "Property",
            "valueType": "xs:string",
            "value": "FH Technikum Wien"
          },
          {
            "idShort": "Street",
            "modelType": "Property",
            "valueType": "xs:string",
            "value": "Höchstädtplatz 6"
          },
          {
            "idShort": "Zipcode",
            "modelType": "Property",
            "valueType": "xs:string",
            "value": "1200"
          },
          {
            "idShort": "CityTown",
            "modelType": "Property",
            "valueType": "xs:string",
            "value": "Wien"
          },
          {
            "idShort": "NationalCode",
            "modelType": "Property",
            "valueType": "xs:string",
            "value": "AUT"
          },
          {
            "idShort": "StateCounty",
            "modelType": "Property",
            "valueType": "xs:string",
            "value": "Wien"
          },
          {
            "idShort": "Office",
            "modelType": "Property",
            "valueType": "xs:string",
            "value": "+43 1 333 40 77 - 7960"
          },
          {
            "idShort": "Email",
            "modelType": "Property",
            "valueType": "xs:string",
            "value": "info.bmr@technikum-wien.at"
          },
          {
            "idShort": "Website",
            "modelType": "Property",
            "valueType": "xs:string",
            "value": "https://www.technikum-wien.at/"
          }
        ]
      },
        {
          "value": "Mechatronische Sortiermaschine",
          "idShort": "ProductName",
          "category": "PARAMETER",
          "modelType": "Property",
          "valueType": "xs:string",
          "semanticId": {
            "keys": [
              {
                "type": "ConceptDescription",
                "value": "0173-1#02-AAP906#001"
              }
            ],
            "type": "ModelReference"
          },
          "description": []
        },
        {
          "value": "Mechatronische Sortiermaschine",
          "idShort": "Productname/SerialNumber",
          "category": "PARAMETER",
          "modelType": "Property",
          "valueType": "xs:string",
          "semanticId": {
            "keys": [
              {
                "type": "ConceptDescription",
                "value": "www.company.com/ids/cd/9544_4082_7091_8596"
              }
            ],
            "type": "ModelReference"
          },
          "description": []
        },
        {
          "value": "Sortiermaschine",
          "idShort": "ManufacturerProductFamily",
          "category": "PARAMETER",
          "modelType": "Property",
          "valueType": "xs:string",
          "semanticId": {
            "keys": [
              {
                "type": "ConceptDescription",
                "value": "https://www.hsu-hh.de/aut/aas/manufacturerproductfamily"
              }
            ],
            "type": "ModelReference"
          },
          "description": []
        },
        {
          "value": "Mechatronical sortingmachine",
          "idShort": "ManufacturerProductDesignation",
          "category": "PARAMETER",
          "modelType": "Property",
          "valueType": "xs:string",
          "semanticId": {
            "keys": [
              {
                "type": "ConceptDescription",
                "value": "https://www.hsu-hh.de/aut/aas/manufacturerproductdesignation"
              }
            ],
            "type": "ModelReference"
          },
          "description": []
        },
        {
          "value": "2022",
          "idShort": "YearOfConstruction",
          "category": "PARAMETER",
          "modelType": "Property",
          "valueType": "xs:string",
          "semanticId": {
            "keys": [
              {
                "type": "ConceptDescription",
                "value": "0173-1#02-AAP906#001"
              }
            ],
            "type": "ModelReference"
          },
          "description": []
        },
        {
          "value": [
            {
              "value": "",
              "idShort": "CEMarkingPresent",
              "category": "PARAMETER",
              "modelType": "Property",
              "valueType": "xs:string",
              "semanticId": {
                "keys": [
                  {
                    "type": "ConceptDescription",
                    "value": "0173-1#02-AAX043#001"
                  }
                ],
                "type": "ModelReference"
              },
              "description": []
            },
            {
              "value": "",
              "idShort": "File",
              "category": "PARAMETER",
              "modelType": "File",
              "semanticId": {
                "keys": [
                  {
                    "type": "ConceptDescription",
                    "value": "0173-1#02-AAD005#008"
                  }
                ],
                "type": "ModelReference"
              },
              "contentType": "",
              "description": []
            }
          ],
          "idShort": "Marking_CE",
          "category": "PARAMETER",
          "modelType": "SubmodelElementCollection",
          "semanticId": {
            "keys": [
              {
                "type": "ConceptDescription",
                "value": "https://www.hsu-hh.de/aut/aas/productmarking"
              }
            ],
            "type": "ModelReference"
          },
          "description": []
        },
        {
          "value": [
            {
              "value": "",
              "idShort": "CRUUSLabelingPresent",
              "category": "PARAMETER",
              "modelType": "Property",
              "valueType": "xs:string",
              "semanticId": {
                "keys": [
                  {
                    "type": "ConceptDescription",
                    "value": "0173-1#02-AAR528#005"
                  }
                ],
                "type": "ModelReference"
              },
              "description": []
            },
            {
              "idShort": "File",
              "category": "PARAMETER",
              "modelType": "File",
              "semanticId": {
                "keys": [
                  {
                    "type": "ConceptDescription",
                    "value": "0173-1#02-AAD005#008"
                  }
                ],
                "type": "ModelReference"
              },
              "contentType": "",
              "description": []
            }
          ],
          "idShort": "Marking_CRUUS",
          "category": "PARAMETER",
          "modelType": "SubmodelElementCollection",
          "semanticId": {
            "keys": [
              {
                "type": "ConceptDescription",
                "value": "https://www.hsu-hh.de/aut/aas/productmarking"
              }
            ],
            "type": "ModelReference"
          },
          "description": []
        },
        {
          "value": [
            {
              "value": "",
              "idShort": "RCMLabelingPresent",
              "category": "PARAMETER",
              "modelType": "Property",
              "valueType": "xs:string",
              "semanticId": {
                "keys": [
                  {
                    "type": "ConceptDescription",
                    "value": "0173-1#02-AAR528#005"
                  }
                ],
                "type": "ModelReference"
              },
              "description": []
            },
            {
              "idShort": "File",
              "category": "PARAMETER",
              "modelType": "File",
              "semanticId": {
                "keys": [
                  {
                    "type": "ConceptDescription",
                    "value": "0173-1#02-AAD005#008"
                  }
                ],
                "type": "ModelReference"
              },
              "contentType": "",
              "description": []
            }
          ],
          "idShort": "Marking_RCM",
          "category": "PARAMETER",
          "modelType": "SubmodelElementCollection",
          "semanticId": {
            "keys": [
              {
                "type": "ConceptDescription",
                "value": "https://www.hsu-hh.de/aut/aas/productmarking"
              }
            ],
            "type": "ModelReference"
          },
          "description": []
        }
      ]
    },
    {
      "idShort": "Datasheets",
      "id": "https://example.com/ids/sm/9220_0192_5052_9396",
      "semanticId": {
        "type": "ModelReference",
        "keys": [
          {
            "type": "Submodel",
            "value": "http://admin-shell.io/vdi/2770/1/0/Documentation"
          }
        ]
      },
      "submodelElements": [
        {
          "category": "CONSTANT",
          "idShort": "micro motors E192-24-49",
          "semanticId": {
            "type": "ExternalReference",
            "keys": [
              {
                "type": "GlobalReference",
                "value": "http://admin-shell.io/vdi/2770/1/0/Document"
              }
            ]
          },
          "value": [
            {
              "category": "CONSTANT",
              "idShort": "DocumentId",
              "semanticId": {
                "type": "ExternalReference",
                "keys": [
                  {
                    "type": "GlobalReference",
                    "value": "http://admin-shell.io/vdi/2770/1/0/DocumentId/Id"
                  }
                ]
              },
              "valueType": "xs:string",
              "value": "RS877-7152",
              "modelType": "Property"
            },
            {
              "category": "CONSTANT",
              "idShort": "ClassId",
              "semanticId": {
                "type": "ExternalReference",
                "keys": [
                  {
                    "type": "GlobalReference",
                    "value": "http://admin-shell.io/vdi/2770/1/0/DocumentClassification/ClassId"
                  }
                ]
              },
              "valueType": "xs:string",
              "value": "02-01",
              "modelType": "Property"
            },
            {
              "category": "CONSTANT",
              "idShort": "ClassName",
              "semanticId": {
                "type": "ExternalReference",
                "keys": [
                  {
                    "type": "GlobalReference",
                    "value": "http://admin-shell.io/vdi/2770/1/0/DocumentClassification/ClassName"
                  }
                ]
              },
              "valueType": "xs:string",
              "value": "Technical specifiction",
              "modelType": "Property"
            },
            {
              "category": "CONSTANT",
              "idShort": "ClassificationSystem",
              "semanticId": {
                "type": "ExternalReference",
                "keys": [
                  {
                    "type": "GlobalReference",
                    "value": "http://admin-shell.io/vdi/2770/1/0/DocumentClassification/ClassificationSystem"
                  }
                ]
              },
              "valueType": "xs:string",
              "value": "VDI2770:2018",
              "modelType": "Property"
            },
            {
              "category": "CONSTANT",
              "idShort": "DocumentVersion{0:00}",
              "semanticId": {
                "type": "ExternalReference",
                "keys": [
                  {
                    "type": "GlobalReference",
                    "value": "http://admin-shell.io/vdi/2770/1/0/DocumentVersion"
                  }
                ]
              },
              "value": [
                {
                  "category": "CONSTANT",
                  "idShort": "Title",
                  "semanticId": {
                    "type": "ExternalReference",
                    "keys": [
                      {
                        "type": "GlobalReference",
                        "value": "http://admin-shell.io/vdi/2770/1/0/Description/Title"
                      }
                    ]
                  },
                  "value": [
                    {
                      "language": "en",
                      "text": "Technical Data RS 877-7152 24Vdc 60RPM"
                    },
                    {
                      "language": "de",
                      "text": "Technisches Datenblatt RS 877-7152 24Vdc 60RPM"
                    }
                  ],
                  "modelType": "MultiLanguageProperty"
                },
                {
                  "category": "CONSTANT",
                  "idShort": "DigitalFile{0:00}",
                  "semanticId": {
                    "type": "ExternalReference",
                    "keys": [
                      {
                        "type": "GlobalReference",
                        "value": "http://admin-shell.io/vdi/2770/1/0/StoredDocumentRepresentation/DigitalFile"
                      }
                    ]
                  },
                  "value": "https://ywheivlrppourvacbxkz.supabase.co/storage/v1/object/public/datasheets/motors/micro_motors_E192-24-49.pdf",
                  "contentType": "EMPTY",
                  "modelType": "File"
                },
                {
                  "category": "CONSTANT",
                  "idShort": "SetDate",
                  "semanticId": {
                    "type": "ExternalReference",
                    "keys": [
                      {
                        "type": "GlobalReference",
                        "value": "http://admin-shell.io/vdi/2770/1/0/LifeCycleStatus/SetDate"
                      }
                    ]
                  },
                  "valueType": "xs:string",
                  "value": "18.05.2025",
                  "modelType": "Property"
                },
                {
                  "category": "CONSTANT",
                  "idShort": "OrganizationName",
                  "semanticId": {
                    "type": "ExternalReference",
                    "keys": [
                      {
                        "type": "GlobalReference",
                        "value": "http://admin-shell.io/vdi/2770/1/0/Organization/OrganizationName"
                      }
                    ]
                  },
                  "valueType": "xs:string",
                  "value": "micro motors s.r.l.",
                  "modelType": "Property"
                }
              ],
              "modelType": "SubmodelElementCollection"
            }
          ],
          "modelType": "SubmodelElementCollection"
        },
        {
          "category": "CONSTANT",
          "idShort": "micro motors E192.24.336",
          "semanticId": {
            "type": "ExternalReference",
            "keys": [
              {
                "type": "GlobalReference",
                "value": "http://admin-shell.io/vdi/2770/1/0/Document"
              }
            ]
          },
          "value": [
            {
              "category": "CONSTANT",
              "idShort": "DocumentId",
              "semanticId": {
                "type": "ExternalReference",
                "keys": [
                  {
                    "type": "GlobalReference",
                    "value": "http://admin-shell.io/vdi/2770/1/0/DocumentId/Id"
                  }
                ]
              },
              "valueType": "xs:string",
              "value": "E192.24.336",
              "modelType": "Property"
            },
            {
              "category": "CONSTANT",
              "idShort": "ClassId",
              "semanticId": {
                "type": "ExternalReference",
                "keys": [
                  {
                    "type": "GlobalReference",
                    "value": "http://admin-shell.io/vdi/2770/1/0/DocumentClassification/ClassId"
                  }
                ]
              },
              "valueType": "xs:string",
              "value": "02-01",
              "modelType": "Property"
            },
            {
              "category": "CONSTANT",
              "idShort": "ClassName",
              "semanticId": {
                "type": "ExternalReference",
                "keys": [
                  {
                    "type": "GlobalReference",
                    "value": "http://admin-shell.io/vdi/2770/1/0/DocumentClassification/ClassName"
                  }
                ]
              },
              "valueType": "xs:string",
              "value": "Technical specifiction",
              "modelType": "Property"
            },
            {
              "category": "CONSTANT",
              "idShort": "ClassificationSystem",
              "semanticId": {
                "type": "ExternalReference",
                "keys": [
                  {
                    "type": "GlobalReference",
                    "value": "http://admin-shell.io/vdi/2770/1/0/DocumentClassification/ClassificationSystem"
                  }
                ]
              },
              "valueType": "xs:string",
              "value": "VDI2770:2018",
              "modelType": "Property"
            },
            {
              "category": "CONSTANT",
              "idShort": "DocumentVersion{0:00}",
              "semanticId": {
                "type": "ExternalReference",
                "keys": [
                  {
                    "type": "GlobalReference",
                    "value": "http://admin-shell.io/vdi/2770/1/0/DocumentVersion"
                  }
                ]
              },
              "value": [
                {
                  "category": "CONSTANT",
                  "idShort": "Title",
                  "semanticId": {
                    "type": "ExternalReference",
                    "keys": [
                      {
                        "type": "GlobalReference",
                        "value": "http://admin-shell.io/vdi/2770/1/0/Description/Title"
                      }
                    ]
                  },
                  "value": [
                    {
                      "language": "de",
                      "text": "Technisches Datenblatt E192.24.336"
                    },
                    {
                      "language": "en",
                      "text": "Technical Datasheet E192.24.336"
                    }
                  ],
                  "modelType": "MultiLanguageProperty"
                },
                {
                  "category": "CONSTANT",
                  "idShort": "DigitalFile{0:00}",
                  "semanticId": {
                    "type": "ExternalReference",
                    "keys": [
                      {
                        "type": "GlobalReference",
                        "value": "http://admin-shell.io/vdi/2770/1/0/StoredDocumentRepresentation/DigitalFile"
                      }
                    ]
                  },
                  "value": "https://ywheivlrppourvacbxkz.supabase.co/storage/v1/object/public/datasheets/motors/micro_motors_E192.24.336.pdf",
                  "contentType": "EMPTY",
                  "modelType": "File"
                },
                {
                  "category": "CONSTANT",
                  "idShort": "SetDate",
                  "semanticId": {
                    "type": "ExternalReference",
                    "keys": [
                      {
                        "type": "GlobalReference",
                        "value": "http://admin-shell.io/vdi/2770/1/0/LifeCycleStatus/SetDate"
                      }
                    ]
                  },
                  "valueType": "xs:string",
                  "value": "18.05.2025",
                  "modelType": "Property"
                },
                {
                  "category": "CONSTANT",
                  "idShort": "OrganizationName",
                  "semanticId": {
                    "type": "ExternalReference",
                    "keys": [
                      {
                        "type": "GlobalReference",
                        "value": "http://admin-shell.io/vdi/2770/1/0/Organization/OrganizationName"
                      }
                    ]
                  },
                  "valueType": "xs:string",
                  "value": "micro motors s.r.l.",
                  "modelType": "Property"
                }
              ],
              "modelType": "SubmodelElementCollection"
            }
          ],
          "modelType": "SubmodelElementCollection"
        },
        {
          "category": "CONSTANT",
          "idShort": "SMC LEY16B-100-S1CL18",
          "semanticId": {
            "type": "ExternalReference",
            "keys": [
              {
                "type": "GlobalReference",
                "value": "http://admin-shell.io/vdi/2770/1/0/Document"
              }
            ]
          },
          "value": [
            {
              "category": "CONSTANT",
              "idShort": "DocumentId",
              "semanticId": {
                "type": "ExternalReference",
                "keys": [
                  {
                    "type": "GlobalReference",
                    "value": "http://admin-shell.io/vdi/2770/1/0/DocumentId/Id"
                  }
                ]
              },
              "valueType": "xs:string",
              "value": "LEY16B-100-S1CL18",
              "modelType": "Property"
            },
            {
              "category": "CONSTANT",
              "idShort": "ClassId",
              "semanticId": {
                "type": "ExternalReference",
                "keys": [
                  {
                    "type": "GlobalReference",
                    "value": "http://admin-shell.io/vdi/2770/1/0/DocumentClassification/ClassId"
                  }
                ]
              },
              "valueType": "xs:string",
              "value": "02-01",
              "modelType": "Property"
            },
            {
              "category": "CONSTANT",
              "idShort": "ClassName",
              "semanticId": {
                "type": "ExternalReference",
                "keys": [
                  {
                    "type": "GlobalReference",
                    "value": "http://admin-shell.io/vdi/2770/1/0/DocumentClassification/ClassName"
                  }
                ]
              },
              "valueType": "xs:string",
              "value": "Technical specifiction",
              "modelType": "Property"
            },
            {
              "category": "CONSTANT",
              "idShort": "ClassificationSystem",
              "semanticId": {
                "type": "ExternalReference",
                "keys": [
                  {
                    "type": "GlobalReference",
                    "value": "http://admin-shell.io/vdi/2770/1/0/DocumentClassification/ClassificationSystem"
                  }
                ]
              },
              "valueType": "xs:string",
              "value": "VDI2770:2018",
              "modelType": "Property"
            },
            {
              "category": "CONSTANT",
              "idShort": "DocumentVersion{0:00}",
              "semanticId": {
                "type": "ExternalReference",
                "keys": [
                  {
                    "type": "GlobalReference",
                    "value": "http://admin-shell.io/vdi/2770/1/0/DocumentVersion"
                  }
                ]
              },
              "value": [
                {
                  "category": "CONSTANT",
                  "idShort": "Title",
                  "semanticId": {
                    "type": "ExternalReference",
                    "keys": [
                      {
                        "type": "GlobalReference",
                        "value": "http://admin-shell.io/vdi/2770/1/0/Description/Title"
                      }
                    ]
                  },
                  "value": [
                    {
                      "language": "de",
                      "text": "LEY16B-100-S1CL18"
                    }
                  ],
                  "modelType": "MultiLanguageProperty"
                },
                {
                  "category": "CONSTANT",
                  "idShort": "DigitalFile{0:00}",
                  "semanticId": {
                    "type": "ExternalReference",
                    "keys": [
                      {
                        "type": "GlobalReference",
                        "value": "http://admin-shell.io/vdi/2770/1/0/StoredDocumentRepresentation/DigitalFile"
                      }
                    ]
                  },
                  "value": "https://ywheivlrppourvacbxkz.supabase.co/storage/v1/object/public/datasheets/motors/SMC_LEY16B-100-S1CL18.pdf",
                  "contentType": "EMPTY",
                  "modelType": "File"
                },
                {
                  "category": "CONSTANT",
                  "idShort": "SetDate",
                  "semanticId": {
                    "type": "ExternalReference",
                    "keys": [
                      {
                        "type": "GlobalReference",
                        "value": "http://admin-shell.io/vdi/2770/1/0/LifeCycleStatus/SetDate"
                      }
                    ]
                  },
                  "valueType": "xs:string",
                  "value": "18.05.2025",
                  "modelType": "Property"
                },
                {
                  "category": "CONSTANT",
                  "idShort": "OrganizationName",
                  "semanticId": {
                    "type": "ExternalReference",
                    "keys": [
                      {
                        "type": "GlobalReference",
                        "value": "http://admin-shell.io/vdi/2770/1/0/Organization/OrganizationName"
                      }
                    ]
                  },
                  "valueType": "xs:string",
                  "value": "SMC Austria GmbH",
                  "modelType": "Property"
                }
              ],
              "modelType": "SubmodelElementCollection"
            }
          ],
          "modelType": "SubmodelElementCollection"
        },
        {
          "category": "CONSTANT",
          "idShort": "SMC LEYG16MB-100-S1CL18",
          "semanticId": {
            "type": "ExternalReference",
            "keys": [
              {
                "type": "GlobalReference",
                "value": "http://admin-shell.io/vdi/2770/1/0/Document"
              }
            ]
          },
          "value": [
            {
              "category": "CONSTANT",
              "idShort": "DocumentId",
              "semanticId": {
                "type": "ExternalReference",
                "keys": [
                  {
                    "type": "GlobalReference",
                    "value": "http://admin-shell.io/vdi/2770/1/0/DocumentId/Id"
                  }
                ]
              },
              "valueType": "xs:string",
              "value": "LEYG16MB-100-S1CL18",
              "modelType": "Property"
            },
            {
              "category": "CONSTANT",
              "idShort": "ClassId",
              "semanticId": {
                "type": "ExternalReference",
                "keys": [
                  {
                    "type": "GlobalReference",
                    "value": "http://admin-shell.io/vdi/2770/1/0/DocumentClassification/ClassId"
                  }
                ]
              },
              "valueType": "xs:string",
              "value": "02-01",
              "modelType": "Property"
            },
            {
              "category": "CONSTANT",
              "idShort": "ClassName",
              "semanticId": {
                "type": "ExternalReference",
                "keys": [
                  {
                    "type": "GlobalReference",
                    "value": "http://admin-shell.io/vdi/2770/1/0/DocumentClassification/ClassName"
                  }
                ]
              },
              "valueType": "xs:string",
              "value": "Technical specifiction",
              "modelType": "Property"
            },
            {
              "category": "CONSTANT",
              "idShort": "ClassificationSystem",
              "semanticId": {
                "type": "ExternalReference",
                "keys": [
                  {
                    "type": "GlobalReference",
                    "value": "http://admin-shell.io/vdi/2770/1/0/DocumentClassification/ClassificationSystem"
                  }
                ]
              },
              "valueType": "xs:string",
              "value": "VDI2770:2018",
              "modelType": "Property"
            },
            {
              "category": "CONSTANT",
              "idShort": "DocumentVersion{0:00}",
              "semanticId": {
                "type": "ExternalReference",
                "keys": [
                  {
                    "type": "GlobalReference",
                    "value": "http://admin-shell.io/vdi/2770/1/0/DocumentVersion"
                  }
                ]
              },
              "value": [
                {
                  "category": "CONSTANT",
                  "idShort": "Title",
                  "semanticId": {
                    "type": "ExternalReference",
                    "keys": [
                      {
                        "type": "GlobalReference",
                        "value": "http://admin-shell.io/vdi/2770/1/0/Description/Title"
                      }
                    ]
                  },
                  "value": [
                    {
                      "language": "de",
                      "text": "LEYG16MB-100-S1CL18"
                    }
                  ],
                  "modelType": "MultiLanguageProperty"
                },
                {
                  "category": "CONSTANT",
                  "idShort": "DigitalFile{0:00}",
                  "semanticId": {
                    "type": "ExternalReference",
                    "keys": [
                      {
                        "type": "GlobalReference",
                        "value": "http://admin-shell.io/vdi/2770/1/0/StoredDocumentRepresentation/DigitalFile"
                      }
                    ]
                  },
                  "value": "https://ywheivlrppourvacbxkz.supabase.co/storage/v1/object/public/datasheets/motors/SMC_LEYG16MB-100-S1CL18.pdf",
                  "contentType": "EMPTY",
                  "modelType": "File"
                },
                {
                  "category": "CONSTANT",
                  "idShort": "SetDate",
                  "semanticId": {
                    "type": "ExternalReference",
                    "keys": [
                      {
                        "type": "GlobalReference",
                        "value": "http://admin-shell.io/vdi/2770/1/0/LifeCycleStatus/SetDate"
                      }
                    ]
                  },
                  "valueType": "xs:string",
                  "value": "18.05.2025",
                  "modelType": "Property"
                },
                {
                  "category": "CONSTANT",
                  "idShort": "OrganizationName",
                  "semanticId": {
                    "type": "ExternalReference",
                    "keys": [
                      {
                        "type": "GlobalReference",
                        "value": "http://admin-shell.io/vdi/2770/1/0/Organization/OrganizationName"
                      }
                    ]
                  },
                  "valueType": "xs:string",
                  "value": "SMC Austria GmbH",
                  "modelType": "Property"
                }
              ],
              "modelType": "SubmodelElementCollection"
            }
          ],
          "modelType": "SubmodelElementCollection"
        },
        {
          "category": "CONSTANT",
          "idShort": "Siemens Simatic S7-1200 CPU 1215C",
          "semanticId": {
            "type": "ExternalReference",
            "keys": [
              {
                "type": "GlobalReference",
                "value": "http://admin-shell.io/vdi/2770/1/0/Document"
              }
            ]
          },
          "value": [
            {
              "category": "CONSTANT",
              "idShort": "DocumentId",
              "semanticId": {
                "type": "ExternalReference",
                "keys": [
                  {
                    "type": "GlobalReference",
                    "value": "http://admin-shell.io/vdi/2770/1/0/DocumentId/Id"
                  }
                ]
              },
              "valueType": "xs:string",
              "value": "Simatic S7-1200 CPU 1215C",
              "modelType": "Property"
            },
            {
              "category": "CONSTANT",
              "idShort": "ClassId",
              "semanticId": {
                "type": "ExternalReference",
                "keys": [
                  {
                    "type": "GlobalReference",
                    "value": "http://admin-shell.io/vdi/2770/1/0/DocumentClassification/ClassId"
                  }
                ]
              },
              "valueType": "xs:string",
              "value": "02-01",
              "modelType": "Property"
            },
            {
              "category": "CONSTANT",
              "idShort": "ClassName",
              "semanticId": {
                "type": "ExternalReference",
                "keys": [
                  {
                    "type": "GlobalReference",
                    "value": "http://admin-shell.io/vdi/2770/1/0/DocumentClassification/ClassName"
                  }
                ]
              },
              "valueType": "xs:string",
              "value": "Technical specifiction",
              "modelType": "Property"
            },
            {
              "category": "CONSTANT",
              "idShort": "ClassificationSystem",
              "semanticId": {
                "type": "ExternalReference",
                "keys": [
                  {
                    "type": "GlobalReference",
                    "value": "http://admin-shell.io/vdi/2770/1/0/DocumentClassification/ClassificationSystem"
                  }
                ]
              },
              "valueType": "xs:string",
              "value": "VDI2770:2018",
              "modelType": "Property"
            },
            {
              "category": "CONSTANT",
              "idShort": "DocumentVersion{0:00}",
              "semanticId": {
                "type": "ExternalReference",
                "keys": [
                  {
                    "type": "GlobalReference",
                    "value": "http://admin-shell.io/vdi/2770/1/0/DocumentVersion"
                  }
                ]
              },
              "value": [
                {
                  "category": "CONSTANT",
                  "idShort": "Title",
                  "semanticId": {
                    "type": "ExternalReference",
                    "keys": [
                      {
                        "type": "GlobalReference",
                        "value": "http://admin-shell.io/vdi/2770/1/0/Description/Title"
                      }
                    ]
                  },
                  "value": [
                    {
                      "language": "de",
                      "text": "Simatic S7-1200 CPU 1215C"
                    }
                  ],
                  "modelType": "MultiLanguageProperty"
                },
                {
                  "category": "CONSTANT",
                  "idShort": "DigitalFile{0:00}",
                  "semanticId": {
                    "type": "ExternalReference",
                    "keys": [
                      {
                        "type": "GlobalReference",
                        "value": "http://admin-shell.io/vdi/2770/1/0/StoredDocumentRepresentation/DigitalFile"
                      }
                    ]
                  },
                  "value": "https://ywheivlrppourvacbxkz.supabase.co/storage/v1/object/public/datasheets/devices/Siemens_Simatic_S7-1200_CPU_1215C.pdf",
                  "contentType": "EMPTY",
                  "modelType": "File"
                },
                {
                  "category": "CONSTANT",
                  "idShort": "SetDate",
                  "semanticId": {
                    "type": "ExternalReference",
                    "keys": [
                      {
                        "type": "GlobalReference",
                        "value": "http://admin-shell.io/vdi/2770/1/0/LifeCycleStatus/SetDate"
                      }
                    ]
                  },
                  "valueType": "xs:string",
                  "value": "18.05.2025",
                  "modelType": "Property"
                },
                {
                  "category": "CONSTANT",
                  "idShort": "OrganizationName",
                  "semanticId": {
                    "type": "ExternalReference",
                    "keys": [
                      {
                        "type": "GlobalReference",
                        "value": "http://admin-shell.io/vdi/2770/1/0/Organization/OrganizationName"
                      }
                    ]
                  },
                  "valueType": "xs:string",
                  "value": "Siemens Aktiengesellschaft \u00D6sterreich",
                  "modelType": "Property"
                }
              ],
              "modelType": "SubmodelElementCollection"
            }
          ],
          "modelType": "SubmodelElementCollection"
        },
        {
          "category": "CONSTANT",
          "idShort": "SICK SIG200-0A0412200",
          "semanticId": {
            "type": "ExternalReference",
            "keys": [
              {
                "type": "GlobalReference",
                "value": "http://admin-shell.io/vdi/2770/1/0/Document"
              }
            ]
          },
          "value": [
            {
              "category": "CONSTANT",
              "idShort": "DocumentId",
              "semanticId": {
                "type": "ExternalReference",
                "keys": [
                  {
                    "type": "GlobalReference",
                    "value": "http://admin-shell.io/vdi/2770/1/0/DocumentId/Id"
                  }
                ]
              },
              "valueType": "xs:string",
              "value": "SIG200-0A0412200",
              "modelType": "Property"
            },
            {
              "category": "CONSTANT",
              "idShort": "ClassId",
              "semanticId": {
                "type": "ExternalReference",
                "keys": [
                  {
                    "type": "GlobalReference",
                    "value": "http://admin-shell.io/vdi/2770/1/0/DocumentClassification/ClassId"
                  }
                ]
              },
              "valueType": "xs:string",
              "value": "02-01",
              "modelType": "Property"
            },
            {
              "category": "CONSTANT",
              "idShort": "ClassName",
              "semanticId": {
                "type": "ExternalReference",
                "keys": [
                  {
                    "type": "GlobalReference",
                    "value": "http://admin-shell.io/vdi/2770/1/0/DocumentClassification/ClassName"
                  }
                ]
              },
              "valueType": "xs:string",
              "value": "Technical specifiction",
              "modelType": "Property"
            },
            {
              "category": "CONSTANT",
              "idShort": "ClassificationSystem",
              "semanticId": {
                "type": "ExternalReference",
                "keys": [
                  {
                    "type": "GlobalReference",
                    "value": "http://admin-shell.io/vdi/2770/1/0/DocumentClassification/ClassificationSystem"
                  }
                ]
              },
              "valueType": "xs:string",
              "value": "VDI2770:2018",
              "modelType": "Property"
            },
            {
              "category": "CONSTANT",
              "idShort": "DocumentVersion{0:00}",
              "semanticId": {
                "type": "ExternalReference",
                "keys": [
                  {
                    "type": "GlobalReference",
                    "value": "http://admin-shell.io/vdi/2770/1/0/DocumentVersion"
                  }
                ]
              },
              "value": [
                {
                  "category": "CONSTANT",
                  "idShort": "Title",
                  "semanticId": {
                    "type": "ExternalReference",
                    "keys": [
                      {
                        "type": "GlobalReference",
                        "value": "http://admin-shell.io/vdi/2770/1/0/Description/Title"
                      }
                    ]
                  },
                  "value": [
                    {
                      "language": "de",
                      "text": "SIG200-0A0412200"
                    }
                  ],
                  "modelType": "MultiLanguageProperty"
                },
                {
                  "category": "CONSTANT",
                  "idShort": "DigitalFile{0:00}",
                  "semanticId": {
                    "type": "ExternalReference",
                    "keys": [
                      {
                        "type": "GlobalReference",
                        "value": "http://admin-shell.io/vdi/2770/1/0/StoredDocumentRepresentation/DigitalFile"
                      }
                    ]
                  },
                  "value": "https://ywheivlrppourvacbxkz.supabase.co/storage/v1/object/public/datasheets/devices/PROFINET_SICK_SIG200-0A0412200.pdf",
                  "contentType": "EMPTY",
                  "modelType": "File"
                },
                {
                  "category": "CONSTANT",
                  "idShort": "SetDate",
                  "semanticId": {
                    "type": "ExternalReference",
                    "keys": [
                      {
                        "type": "GlobalReference",
                        "value": "http://admin-shell.io/vdi/2770/1/0/LifeCycleStatus/SetDate"
                      }
                    ]
                  },
                  "valueType": "xs:string",
                  "value": "18.05.2025",
                  "modelType": "Property"
                },
                {
                  "category": "CONSTANT",
                  "idShort": "OrganizationName",
                  "semanticId": {
                    "type": "ExternalReference",
                    "keys": [
                      {
                        "type": "GlobalReference",
                        "value": "http://admin-shell.io/vdi/2770/1/0/Organization/OrganizationName"
                      }
                    ]
                  },
                  "valueType": "xs:string",
                  "value": "SICK AG",
                  "modelType": "Property"
                }
              ],
              "modelType": "SubmodelElementCollection"
            }
          ],
          "modelType": "SubmodelElementCollection"
        },
        {
          "category": "CONSTANT",
          "idShort": "SICK SIM4000-0P03G10",
          "semanticId": {
            "type": "ExternalReference",
            "keys": [
              {
                "type": "GlobalReference",
                "value": "http://admin-shell.io/vdi/2770/1/0/Document"
              }
            ]
          },
          "value": [
            {
              "category": "CONSTANT",
              "idShort": "DocumentId",
              "semanticId": {
                "type": "ExternalReference",
                "keys": [
                  {
                    "type": "GlobalReference",
                    "value": "http://admin-shell.io/vdi/2770/1/0/DocumentId/Id"
                  }
                ]
              },
              "valueType": "xs:string",
              "value": "SIM4000-0P03G10",
              "modelType": "Property"
            },
            {
              "category": "CONSTANT",
              "idShort": "ClassId",
              "semanticId": {
                "type": "ExternalReference",
                "keys": [
                  {
                    "type": "GlobalReference",
                    "value": "http://admin-shell.io/vdi/2770/1/0/DocumentClassification/ClassId"
                  }
                ]
              },
              "valueType": "xs:string",
              "value": "02-01",
              "modelType": "Property"
            },
            {
              "category": "CONSTANT",
              "idShort": "ClassName",
              "semanticId": {
                "type": "ExternalReference",
                "keys": [
                  {
                    "type": "GlobalReference",
                    "value": "http://admin-shell.io/vdi/2770/1/0/DocumentClassification/ClassName"
                  }
                ]
              },
              "valueType": "xs:string",
              "value": "Technical specifiction",
              "modelType": "Property"
            },
            {
              "category": "CONSTANT",
              "idShort": "ClassificationSystem",
              "semanticId": {
                "type": "ExternalReference",
                "keys": [
                  {
                    "type": "GlobalReference",
                    "value": "http://admin-shell.io/vdi/2770/1/0/DocumentClassification/ClassificationSystem"
                  }
                ]
              },
              "valueType": "xs:string",
              "value": "VDI2770:2018",
              "modelType": "Property"
            },
            {
              "category": "CONSTANT",
              "idShort": "DocumentVersion{0:00}",
              "semanticId": {
                "type": "ExternalReference",
                "keys": [
                  {
                    "type": "GlobalReference",
                    "value": "http://admin-shell.io/vdi/2770/1/0/DocumentVersion"
                  }
                ]
              },
              "value": [
                {
                  "category": "CONSTANT",
                  "idShort": "Title",
                  "semanticId": {
                    "type": "ExternalReference",
                    "keys": [
                      {
                        "type": "GlobalReference",
                        "value": "http://admin-shell.io/vdi/2770/1/0/Description/Title"
                      }
                    ]
                  },
                  "value": [
                    {
                      "language": "de",
                      "text": "SIM4000-0P03G10"
                    }
                  ],
                  "modelType": "MultiLanguageProperty"
                },
                {
                  "category": "CONSTANT",
                  "idShort": "DigitalFile{0:00}",
                  "semanticId": {
                    "type": "ExternalReference",
                    "keys": [
                      {
                        "type": "GlobalReference",
                        "value": "http://admin-shell.io/vdi/2770/1/0/StoredDocumentRepresentation/DigitalFile"
                      }
                    ]
                  },
                  "value": "https://ywheivlrppourvacbxkz.supabase.co/storage/v1/object/public/datasheets/devices/SICK_SIM4000-0P03G10.pdf",
                  "contentType": "EMPTY",
                  "modelType": "File"
                },
                {
                  "category": "CONSTANT",
                  "idShort": "SetDate",
                  "semanticId": {
                    "type": "ExternalReference",
                    "keys": [
                      {
                        "type": "GlobalReference",
                        "value": "http://admin-shell.io/vdi/2770/1/0/LifeCycleStatus/SetDate"
                      }
                    ]
                  },
                  "valueType": "xs:string",
                  "value": "18.05.2025",
                  "modelType": "Property"
                },
                {
                  "category": "CONSTANT",
                  "idShort": "OrganizationName",
                  "semanticId": {
                    "type": "ExternalReference",
                    "keys": [
                      {
                        "type": "GlobalReference",
                        "value": "http://admin-shell.io/vdi/2770/1/0/Organization/OrganizationName"
                      }
                    ]
                  },
                  "valueType": "xs:string",
                  "value": "SICK AG",
                  "modelType": "Property"
                }
              ],
              "modelType": "SubmodelElementCollection"
            }
          ],
          "modelType": "SubmodelElementCollection"
        },
        {
          "category": "CONSTANT",
          "idShort": "SICK WE4SC-3P2230S04",
          "semanticId": {
            "type": "ExternalReference",
            "keys": [
              {
                "type": "GlobalReference",
                "value": "http://admin-shell.io/vdi/2770/1/0/Document"
              }
            ]
          },
          "value": [
            {
              "category": "CONSTANT",
              "idShort": "DocumentId",
              "semanticId": {
                "type": "ExternalReference",
                "keys": [
                  {
                    "type": "GlobalReference",
                    "value": "http://admin-shell.io/vdi/2770/1/0/DocumentId/Id"
                  }
                ]
              },
              "valueType": "xs:string",
              "value": "WE4SC-3P2230S04",
              "modelType": "Property"
            },
            {
              "category": "CONSTANT",
              "idShort": "ClassId",
              "semanticId": {
                "type": "ExternalReference",
                "keys": [
                  {
                    "type": "GlobalReference",
                    "value": "http://admin-shell.io/vdi/2770/1/0/DocumentClassification/ClassId"
                  }
                ]
              },
              "valueType": "xs:string",
              "value": "02-01",
              "modelType": "Property"
            },
            {
              "category": "CONSTANT",
              "idShort": "ClassName",
              "semanticId": {
                "type": "ExternalReference",
                "keys": [
                  {
                    "type": "GlobalReference",
                    "value": "http://admin-shell.io/vdi/2770/1/0/DocumentClassification/ClassName"
                  }
                ]
              },
              "valueType": "xs:string",
              "value": "Technical specifiction",
              "modelType": "Property"
            },
            {
              "category": "CONSTANT",
              "idShort": "ClassificationSystem",
              "semanticId": {
                "type": "ExternalReference",
                "keys": [
                  {
                    "type": "GlobalReference",
                    "value": "http://admin-shell.io/vdi/2770/1/0/DocumentClassification/ClassificationSystem"
                  }
                ]
              },
              "valueType": "xs:string",
              "value": "VDI2770:2018",
              "modelType": "Property"
            },
            {
              "category": "CONSTANT",
              "idShort": "DocumentVersion{0:00}",
              "semanticId": {
                "type": "ExternalReference",
                "keys": [
                  {
                    "type": "GlobalReference",
                    "value": "http://admin-shell.io/vdi/2770/1/0/DocumentVersion"
                  }
                ]
              },
              "value": [
                {
                  "category": "CONSTANT",
                  "idShort": "Title",
                  "semanticId": {
                    "type": "ExternalReference",
                    "keys": [
                      {
                        "type": "GlobalReference",
                        "value": "http://admin-shell.io/vdi/2770/1/0/Description/Title"
                      }
                    ]
                  },
                  "value": [
                    {
                      "language": "de",
                      "text": "WE4SC-3P2230S04"
                    }
                  ],
                  "modelType": "MultiLanguageProperty"
                },
                {
                  "category": "CONSTANT",
                  "idShort": "DigitalFile{0:00}",
                  "semanticId": {
                    "type": "ExternalReference",
                    "keys": [
                      {
                        "type": "GlobalReference",
                        "value": "http://admin-shell.io/vdi/2770/1/0/StoredDocumentRepresentation/DigitalFile"
                      }
                    ]
                  },
                  "value": "https://ywheivlrppourvacbxkz.supabase.co/storage/v1/object/public/datasheets/sensors/SICK_WE4SC-3P2230S04_2084754.pdf",
                  "contentType": "EMPTY",
                  "modelType": "File"
                },
                {
                  "category": "CONSTANT",
                  "idShort": "SetDate",
                  "semanticId": {
                    "type": "ExternalReference",
                    "keys": [
                      {
                        "type": "GlobalReference",
                        "value": "http://admin-shell.io/vdi/2770/1/0/LifeCycleStatus/SetDate"
                      }
                    ]
                  },
                  "valueType": "xs:string",
                  "value": "18.05.2025",
                  "modelType": "Property"
                },
                {
                  "category": "CONSTANT",
                  "idShort": "OrganizationName",
                  "semanticId": {
                    "type": "ExternalReference",
                    "keys": [
                      {
                        "type": "GlobalReference",
                        "value": "http://admin-shell.io/vdi/2770/1/0/Organization/OrganizationName"
                      }
                    ]
                  },
                  "valueType": "xs:string",
                  "value": "SICK AG",
                  "modelType": "Property"
                }
              ],
              "modelType": "SubmodelElementCollection"
            }
          ],
          "modelType": "SubmodelElementCollection"
        },
        {
          "category": "CONSTANT",
          "idShort": "Kemo Power Control M171 16038DI",
          "semanticId": {
            "type": "ExternalReference",
            "keys": [
              {
                "type": "GlobalReference",
                "value": "http://admin-shell.io/vdi/2770/1/0/Document"
              }
            ]
          },
          "value": [
            {
              "category": "CONSTANT",
              "idShort": "DocumentId",
              "semanticId": {
                "type": "ExternalReference",
                "keys": [
                  {
                    "type": "GlobalReference",
                    "value": "http://admin-shell.io/vdi/2770/1/0/DocumentId/Id"
                  }
                ]
              },
              "valueType": "xs:string",
              "value": "M171",
              "modelType": "Property"
            },
            {
              "category": "CONSTANT",
              "idShort": "ClassId",
              "semanticId": {
                "type": "ExternalReference",
                "keys": [
                  {
                    "type": "GlobalReference",
                    "value": "http://admin-shell.io/vdi/2770/1/0/DocumentClassification/ClassId"
                  }
                ]
              },
              "valueType": "xs:string",
              "value": "02-01",
              "modelType": "Property"
            },
            {
              "category": "CONSTANT",
              "idShort": "ClassName",
              "semanticId": {
                "type": "ExternalReference",
                "keys": [
                  {
                    "type": "GlobalReference",
                    "value": "http://admin-shell.io/vdi/2770/1/0/DocumentClassification/ClassName"
                  }
                ]
              },
              "valueType": "xs:string",
              "value": "Technical specifiction",
              "modelType": "Property"
            },
            {
              "category": "CONSTANT",
              "idShort": "ClassificationSystem",
              "semanticId": {
                "type": "ExternalReference",
                "keys": [
                  {
                    "type": "GlobalReference",
                    "value": "http://admin-shell.io/vdi/2770/1/0/DocumentClassification/ClassificationSystem"
                  }
                ]
              },
              "valueType": "xs:string",
              "value": "VDI2770:2018",
              "modelType": "Property"
            },
            {
              "category": "CONSTANT",
              "idShort": "DocumentVersion{0:00}",
              "semanticId": {
                "type": "ExternalReference",
                "keys": [
                  {
                    "type": "GlobalReference",
                    "value": "http://admin-shell.io/vdi/2770/1/0/DocumentVersion"
                  }
                ]
              },
              "value": [
                {
                  "category": "CONSTANT",
                  "idShort": "Title",
                  "semanticId": {
                    "type": "ExternalReference",
                    "keys": [
                      {
                        "type": "GlobalReference",
                        "value": "http://admin-shell.io/vdi/2770/1/0/Description/Title"
                      }
                    ]
                  },
                  "value": [
                    {
                      "language": "de",
                      "text": "M171"
                    }
                  ],
                  "modelType": "MultiLanguageProperty"
                },
                {
                  "category": "CONSTANT",
                  "idShort": "DigitalFile{0:00}",
                  "semanticId": {
                    "type": "ExternalReference",
                    "keys": [
                      {
                        "type": "GlobalReference",
                        "value": "http://admin-shell.io/vdi/2770/1/0/StoredDocumentRepresentation/DigitalFile"
                      }
                    ]
                  },
                  "value": "https://ywheivlrppourvacbxkz.supabase.co/storage/v1/object/public/datasheets/power%20supplies/Kemo_Power_Control_M171_16038DI.pdf",
                  "contentType": "EMPTY",
                  "modelType": "File"
                },
                {
                  "category": "CONSTANT",
                  "idShort": "SetDate",
                  "semanticId": {
                    "type": "ExternalReference",
                    "keys": [
                      {
                        "type": "GlobalReference",
                        "value": "http://admin-shell.io/vdi/2770/1/0/LifeCycleStatus/SetDate"
                      }
                    ]
                  },
                  "valueType": "xs:string",
                  "value": "18.05.2025",
                  "modelType": "Property"
                },
                {
                  "category": "CONSTANT",
                  "idShort": "OrganizationName",
                  "semanticId": {
                    "type": "ExternalReference",
                    "keys": [
                      {
                        "type": "GlobalReference",
                        "value": "http://admin-shell.io/vdi/2770/1/0/Organization/OrganizationName"
                      }
                    ]
                  },
                  "valueType": "xs:string",
                  "value": "Kemo Electronic GmbH",
                  "modelType": "Property"
                }
              ],
              "modelType": "SubmodelElementCollection"
            }
          ],
          "modelType": "SubmodelElementCollection"
        },
        {
          "category": "CONSTANT",
          "idShort": "RND 315-00011",
          "semanticId": {
            "type": "ExternalReference",
            "keys": [
              {
                "type": "GlobalReference",
                "value": "http://admin-shell.io/vdi/2770/1/0/Document"
              }
            ]
          },
          "value": [
            {
              "category": "CONSTANT",
              "idShort": "DocumentId",
              "semanticId": {
                "type": "ExternalReference",
                "keys": [
                  {
                    "type": "GlobalReference",
                    "value": "http://admin-shell.io/vdi/2770/1/0/DocumentId/Id"
                  }
                ]
              },
              "valueType": "xs:string",
              "value": "RND_315-00011",
              "modelType": "Property"
            },
            {
              "category": "CONSTANT",
              "idShort": "ClassId",
              "semanticId": {
                "type": "ExternalReference",
                "keys": [
                  {
                    "type": "GlobalReference",
                    "value": "http://admin-shell.io/vdi/2770/1/0/DocumentClassification/ClassId"
                  }
                ]
              },
              "valueType": "xs:string",
              "value": "02-01",
              "modelType": "Property"
            },
            {
              "category": "CONSTANT",
              "idShort": "ClassName",
              "semanticId": {
                "type": "ExternalReference",
                "keys": [
                  {
                    "type": "GlobalReference",
                    "value": "http://admin-shell.io/vdi/2770/1/0/DocumentClassification/ClassName"
                  }
                ]
              },
              "valueType": "xs:string",
              "value": "Technical specifiction",
              "modelType": "Property"
            },
            {
              "category": "CONSTANT",
              "idShort": "ClassificationSystem",
              "semanticId": {
                "type": "ExternalReference",
                "keys": [
                  {
                    "type": "GlobalReference",
                    "value": "http://admin-shell.io/vdi/2770/1/0/DocumentClassification/ClassificationSystem"
                  }
                ]
              },
              "valueType": "xs:string",
              "value": "VDI2770:2018",
              "modelType": "Property"
            },
            {
              "category": "CONSTANT",
              "idShort": "DocumentVersion{0:00}",
              "semanticId": {
                "type": "ExternalReference",
                "keys": [
                  {
                    "type": "GlobalReference",
                    "value": "http://admin-shell.io/vdi/2770/1/0/DocumentVersion"
                  }
                ]
              },
              "value": [
                {
                  "category": "CONSTANT",
                  "idShort": "Title",
                  "semanticId": {
                    "type": "ExternalReference",
                    "keys": [
                      {
                        "type": "GlobalReference",
                        "value": "http://admin-shell.io/vdi/2770/1/0/Description/Title"
                      }
                    ]
                  },
                  "value": [
                    {
                      "language": "de",
                      "text": "RND_315-00011"
                    }
                  ],
                  "modelType": "MultiLanguageProperty"
                },
                {
                  "category": "CONSTANT",
                  "idShort": "DigitalFile{0:00}",
                  "semanticId": {
                    "type": "ExternalReference",
                    "keys": [
                      {
                        "type": "GlobalReference",
                        "value": "http://admin-shell.io/vdi/2770/1/0/StoredDocumentRepresentation/DigitalFile"
                      }
                    ]
                  },
                  "value": "https://ywheivlrppourvacbxkz.supabase.co/storage/v1/object/public/datasheets/power%20supplies/RND_315-00011.pdf",
                  "contentType": "EMPTY",
                  "modelType": "File"
                },
                {
                  "category": "CONSTANT",
                  "idShort": "SetDate",
                  "semanticId": {
                    "type": "ExternalReference",
                    "keys": [
                      {
                        "type": "GlobalReference",
                        "value": "http://admin-shell.io/vdi/2770/1/0/LifeCycleStatus/SetDate"
                      }
                    ]
                  },
                  "valueType": "xs:string",
                  "value": "18.05.2025",
                  "modelType": "Property"
                },
                {
                  "category": "CONSTANT",
                  "idShort": "OrganizationName",
                  "semanticId": {
                    "type": "ExternalReference",
                    "keys": [
                      {
                        "type": "GlobalReference",
                        "value": "http://admin-shell.io/vdi/2770/1/0/Organization/OrganizationName"
                      }
                    ]
                  },
                  "valueType": "xs:string",
                  "value": "Distrelec Group AG",
                  "modelType": "Property"
                }
              ],
              "modelType": "SubmodelElementCollection"
            }
          ],
          "modelType": "SubmodelElementCollection"
        },
        {
          "category": "CONSTANT",
          "idShort": "SMC JXCL18-LEY16B-100",
          "semanticId": {
            "type": "ExternalReference",
            "keys": [
              {
                "type": "GlobalReference",
                "value": "http://admin-shell.io/vdi/2770/1/0/Document"
              }
            ]
          },
          "value": [
            {
              "category": "CONSTANT",
              "idShort": "DocumentId",
              "semanticId": {
                "type": "ExternalReference",
                "keys": [
                  {
                    "type": "GlobalReference",
                    "value": "http://admin-shell.io/vdi/2770/1/0/DocumentId/Id"
                  }
                ]
              },
              "valueType": "xs:string",
              "value": "JXCL18_LEY16B_100",
              "modelType": "Property"
            },
            {
              "category": "CONSTANT",
              "idShort": "ClassId",
              "semanticId": {
                "type": "ExternalReference",
                "keys": [
                  {
                    "type": "GlobalReference",
                    "value": "http://admin-shell.io/vdi/2770/1/0/DocumentClassification/ClassId"
                  }
                ]
              },
              "valueType": "xs:string",
              "value": "02-01",
              "modelType": "Property"
            },
            {
              "category": "CONSTANT",
              "idShort": "ClassName",
              "semanticId": {
                "type": "ExternalReference",
                "keys": [
                  {
                    "type": "GlobalReference",
                    "value": "http://admin-shell.io/vdi/2770/1/0/DocumentClassification/ClassName"
                  }
                ]
              },
              "valueType": "xs:string",
              "value": "Technical specifiction",
              "modelType": "Property"
            },
            {
              "category": "CONSTANT",
              "idShort": "ClassificationSystem",
              "semanticId": {
                "type": "ExternalReference",
                "keys": [
                  {
                    "type": "GlobalReference",
                    "value": "http://admin-shell.io/vdi/2770/1/0/DocumentClassification/ClassificationSystem"
                  }
                ]
              },
              "valueType": "xs:string",
              "value": "VDI2770:2018",
              "modelType": "Property"
            },
            {
              "category": "CONSTANT",
              "idShort": "DocumentVersion{0:00}",
              "semanticId": {
                "type": "ExternalReference",
                "keys": [
                  {
                    "type": "GlobalReference",
                    "value": "http://admin-shell.io/vdi/2770/1/0/DocumentVersion"
                  }
                ]
              },
              "value": [
                {
                  "category": "CONSTANT",
                  "idShort": "Title",
                  "semanticId": {
                    "type": "ExternalReference",
                    "keys": [
                      {
                        "type": "GlobalReference",
                        "value": "http://admin-shell.io/vdi/2770/1/0/Description/Title"
                      }
                    ]
                  },
                  "value": [
                    {
                      "language": "de",
                      "text": "JXCL18_LEY16B_100"
                    }
                  ],
                  "modelType": "MultiLanguageProperty"
                },
                {
                  "category": "CONSTANT",
                  "idShort": "DigitalFile{0:00}",
                  "semanticId": {
                    "type": "ExternalReference",
                    "keys": [
                      {
                        "type": "GlobalReference",
                        "value": "http://admin-shell.io/vdi/2770/1/0/StoredDocumentRepresentation/DigitalFile"
                      }
                    ]
                  },
                  "value": "https://ywheivlrppourvacbxkz.supabase.co/storage/v1/object/public/datasheets/io-links/SMC_JXCL18-LEY16B-100.pdf",
                  "contentType": "EMPTY",
                  "modelType": "File"
                },
                {
                  "category": "CONSTANT",
                  "idShort": "SetDate",
                  "semanticId": {
                    "type": "ExternalReference",
                    "keys": [
                      {
                        "type": "GlobalReference",
                        "value": "http://admin-shell.io/vdi/2770/1/0/LifeCycleStatus/SetDate"
                      }
                    ]
                  },
                  "valueType": "xs:string",
                  "value": "18.05.2025",
                  "modelType": "Property"
                },
                {
                  "category": "CONSTANT",
                  "idShort": "OrganizationName",
                  "semanticId": {
                    "type": "ExternalReference",
                    "keys": [
                      {
                        "type": "GlobalReference",
                        "value": "http://admin-shell.io/vdi/2770/1/0/Organization/OrganizationName"
                      }
                    ]
                  },
                  "valueType": "xs:string",
                  "value": "SMC Austria GmbH",
                  "modelType": "Property"
                }
              ],
              "modelType": "SubmodelElementCollection"
            }
          ],
          "modelType": "SubmodelElementCollection"
        },
        {
          "category": "CONSTANT",
          "idShort": "TP-Link TL-WR802N",
          "semanticId": {
            "type": "ExternalReference",
            "keys": [
              {
                "type": "GlobalReference",
                "value": "http://admin-shell.io/vdi/2770/1/0/Document"
              }
            ]
          },
          "value": [
            {
              "category": "CONSTANT",
              "idShort": "DocumentId",
              "semanticId": {
                "type": "ExternalReference",
                "keys": [
                  {
                    "type": "GlobalReference",
                    "value": "http://admin-shell.io/vdi/2770/1/0/DocumentId/Id"
                  }
                ]
              },
              "valueType": "xs:string",
              "value": "TL-WR802N",
              "modelType": "Property"
            },
            {
              "category": "CONSTANT",
              "idShort": "ClassId",
              "semanticId": {
                "type": "ExternalReference",
                "keys": [
                  {
                    "type": "GlobalReference",
                    "value": "http://admin-shell.io/vdi/2770/1/0/DocumentClassification/ClassId"
                  }
                ]
              },
              "valueType": "xs:string",
              "value": "02-01",
              "modelType": "Property"
            },
            {
              "category": "CONSTANT",
              "idShort": "ClassName",
              "semanticId": {
                "type": "ExternalReference",
                "keys": [
                  {
                    "type": "GlobalReference",
                    "value": "http://admin-shell.io/vdi/2770/1/0/DocumentClassification/ClassName"
                  }
                ]
              },
              "valueType": "xs:string",
              "value": "Technical specifiction",
              "modelType": "Property"
            },
            {
              "category": "CONSTANT",
              "idShort": "ClassificationSystem",
              "semanticId": {
                "type": "ExternalReference",
                "keys": [
                  {
                    "type": "GlobalReference",
                    "value": "http://admin-shell.io/vdi/2770/1/0/DocumentClassification/ClassificationSystem"
                  }
                ]
              },
              "valueType": "xs:string",
              "value": "VDI2770:2018",
              "modelType": "Property"
            },
            {
              "category": "CONSTANT",
              "idShort": "DocumentVersion{0:00}",
              "semanticId": {
                "type": "ExternalReference",
                "keys": [
                  {
                    "type": "GlobalReference",
                    "value": "http://admin-shell.io/vdi/2770/1/0/DocumentVersion"
                  }
                ]
              },
              "value": [
                {
                  "category": "CONSTANT",
                  "idShort": "Title",
                  "semanticId": {
                    "type": "ExternalReference",
                    "keys": [
                      {
                        "type": "GlobalReference",
                        "value": "http://admin-shell.io/vdi/2770/1/0/Description/Title"
                      }
                    ]
                  },
                  "value": [
                    {
                      "language": "de",
                      "text": "TL-WR802N"
                    }
                  ],
                  "modelType": "MultiLanguageProperty"
                },
                {
                  "category": "CONSTANT",
                  "idShort": "DigitalFile{0:00}",
                  "semanticId": {
                    "type": "ExternalReference",
                    "keys": [
                      {
                        "type": "GlobalReference",
                        "value": "http://admin-shell.io/vdi/2770/1/0/StoredDocumentRepresentation/DigitalFile"
                      }
                    ]
                  },
                  "value": "https://ywheivlrppourvacbxkz.supabase.co/storage/v1/object/public/datasheets/router/tp-link_TL-WR802N.pdf",
                  "contentType": "EMPTY",
                  "modelType": "File"
                },
                {
                  "category": "CONSTANT",
                  "idShort": "SetDate",
                  "semanticId": {
                    "type": "ExternalReference",
                    "keys": [
                      {
                        "type": "GlobalReference",
                        "value": "http://admin-shell.io/vdi/2770/1/0/LifeCycleStatus/SetDate"
                      }
                    ]
                  },
                  "valueType": "xs:string",
                  "value": "18.05.2025",
                  "modelType": "Property"
                },
                {
                  "category": "CONSTANT",
                  "idShort": "OrganizationName",
                  "semanticId": {
                    "type": "ExternalReference",
                    "keys": [
                      {
                        "type": "GlobalReference",
                        "value": "http://admin-shell.io/vdi/2770/1/0/Organization/OrganizationName"
                      }
                    ]
                  },
                  "valueType": "xs:string",
                  "value": "TP-Link Deutschland GmbH",
                  "modelType": "Property"
                }
              ],
              "modelType": "SubmodelElementCollection"
            }
          ],
          "modelType": "SubmodelElementCollection"
        },
        {
          "category": "CONSTANT",
          "idShort": "finder 95.95.3",
          "semanticId": {
            "type": "ExternalReference",
            "keys": [
              {
                "type": "GlobalReference",
                "value": "http://admin-shell.io/vdi/2770/1/0/Document"
              }
            ]
          },
          "value": [
            {
              "category": "CONSTANT",
              "idShort": "DocumentId",
              "semanticId": {
                "type": "ExternalReference",
                "keys": [
                  {
                    "type": "GlobalReference",
                    "value": "http://admin-shell.io/vdi/2770/1/0/DocumentId/Id"
                  }
                ]
              },
              "valueType": "xs:string",
              "value": "95.95.3",
              "modelType": "Property"
            },
            {
              "category": "CONSTANT",
              "idShort": "ClassId",
              "semanticId": {
                "type": "ExternalReference",
                "keys": [
                  {
                    "type": "GlobalReference",
                    "value": "http://admin-shell.io/vdi/2770/1/0/DocumentClassification/ClassId"
                  }
                ]
              },
              "valueType": "xs:string",
              "value": "02-01",
              "modelType": "Property"
            },
            {
              "category": "CONSTANT",
              "idShort": "ClassName",
              "semanticId": {
                "type": "ExternalReference",
                "keys": [
                  {
                    "type": "GlobalReference",
                    "value": "http://admin-shell.io/vdi/2770/1/0/DocumentClassification/ClassName"
                  }
                ]
              },
              "valueType": "xs:string",
              "value": "Technical specifiction",
              "modelType": "Property"
            },
            {
              "category": "CONSTANT",
              "idShort": "ClassificationSystem",
              "semanticId": {
                "type": "ExternalReference",
                "keys": [
                  {
                    "type": "GlobalReference",
                    "value": "http://admin-shell.io/vdi/2770/1/0/DocumentClassification/ClassificationSystem"
                  }
                ]
              },
              "valueType": "xs:string",
              "value": "VDI2770:2018",
              "modelType": "Property"
            },
            {
              "category": "CONSTANT",
              "idShort": "DocumentVersion{0:00}",
              "semanticId": {
                "type": "ExternalReference",
                "keys": [
                  {
                    "type": "GlobalReference",
                    "value": "http://admin-shell.io/vdi/2770/1/0/DocumentVersion"
                  }
                ]
              },
              "value": [
                {
                  "category": "CONSTANT",
                  "idShort": "Title",
                  "semanticId": {
                    "type": "ExternalReference",
                    "keys": [
                      {
                        "type": "GlobalReference",
                        "value": "http://admin-shell.io/vdi/2770/1/0/Description/Title"
                      }
                    ]
                  },
                  "value": [
                    {
                      "language": "de",
                      "text": "95.95.3"
                    }
                  ],
                  "modelType": "MultiLanguageProperty"
                },
                {
                  "category": "CONSTANT",
                  "idShort": "DigitalFile{0:00}",
                  "semanticId": {
                    "type": "ExternalReference",
                    "keys": [
                      {
                        "type": "GlobalReference",
                        "value": "http://admin-shell.io/vdi/2770/1/0/StoredDocumentRepresentation/DigitalFile"
                      }
                    ]
                  },
                  "value": "https://ywheivlrppourvacbxkz.supabase.co/storage/v1/object/public/datasheets/reley%20socket/finder_95.95.3.pdf",
                  "contentType": "EMPTY",
                  "modelType": "File"
                },
                {
                  "category": "CONSTANT",
                  "idShort": "SetDate",
                  "semanticId": {
                    "type": "ExternalReference",
                    "keys": [
                      {
                        "type": "GlobalReference",
                        "value": "http://admin-shell.io/vdi/2770/1/0/LifeCycleStatus/SetDate"
                      }
                    ]
                  },
                  "valueType": "xs:string",
                  "value": "18.05.2025",
                  "modelType": "Property"
                },
                {
                  "category": "CONSTANT",
                  "idShort": "OrganizationName",
                  "semanticId": {
                    "type": "ExternalReference",
                    "keys": [
                      {
                        "type": "GlobalReference",
                        "value": "http://admin-shell.io/vdi/2770/1/0/Organization/OrganizationName"
                      }
                    ]
                  },
                  "valueType": "xs:string",
                  "value": "FINDER S.p.A. sole proprietorship",
                  "modelType": "Property"
                }
              ],
              "modelType": "SubmodelElementCollection"
            }
          ],
          "modelType": "SubmodelElementCollection"
        },
        {
          "category": "CONSTANT",
          "idShort": "finder 40.52.9.024.000",
          "semanticId": {
            "type": "ExternalReference",
            "keys": [
              {
                "type": "GlobalReference",
                "value": "http://admin-shell.io/vdi/2770/1/0/Document"
              }
            ]
          },
          "value": [
            {
              "category": "CONSTANT",
              "idShort": "DocumentId",
              "semanticId": {
                "type": "ExternalReference",
                "keys": [
                  {
                    "type": "GlobalReference",
                    "value": "http://admin-shell.io/vdi/2770/1/0/DocumentId/Id"
                  }
                ]
              },
              "valueType": "xs:string",
              "value": "40.52.9.024.000",
              "modelType": "Property"
            },
            {
              "category": "CONSTANT",
              "idShort": "ClassId",
              "semanticId": {
                "type": "ExternalReference",
                "keys": [
                  {
                    "type": "GlobalReference",
                    "value": "http://admin-shell.io/vdi/2770/1/0/DocumentClassification/ClassId"
                  }
                ]
              },
              "valueType": "xs:string",
              "value": "02-01",
              "modelType": "Property"
            },
            {
              "category": "CONSTANT",
              "idShort": "ClassName",
              "semanticId": {
                "type": "ExternalReference",
                "keys": [
                  {
                    "type": "GlobalReference",
                    "value": "http://admin-shell.io/vdi/2770/1/0/DocumentClassification/ClassName"
                  }
                ]
              },
              "valueType": "xs:string",
              "value": "Technical specifiction",
              "modelType": "Property"
            },
            {
              "category": "CONSTANT",
              "idShort": "ClassificationSystem",
              "semanticId": {
                "type": "ExternalReference",
                "keys": [
                  {
                    "type": "GlobalReference",
                    "value": "http://admin-shell.io/vdi/2770/1/0/DocumentClassification/ClassificationSystem"
                  }
                ]
              },
              "valueType": "xs:string",
              "value": "VDI2770:2018",
              "modelType": "Property"
            },
            {
              "category": "CONSTANT",
              "idShort": "DocumentVersion{0:00}",
              "semanticId": {
                "type": "ExternalReference",
                "keys": [
                  {
                    "type": "GlobalReference",
                    "value": "http://admin-shell.io/vdi/2770/1/0/DocumentVersion"
                  }
                ]
              },
              "value": [
                {
                  "category": "CONSTANT",
                  "idShort": "Title",
                  "semanticId": {
                    "type": "ExternalReference",
                    "keys": [
                      {
                        "type": "GlobalReference",
                        "value": "http://admin-shell.io/vdi/2770/1/0/Description/Title"
                      }
                    ]
                  },
                  "value": [
                    {
                      "language": "de",
                      "text": "40.52.9.024.000"
                    }
                  ],
                  "modelType": "MultiLanguageProperty"
                },
                {
                  "category": "CONSTANT",
                  "idShort": "DigitalFile{0:00}",
                  "semanticId": {
                    "type": "ExternalReference",
                    "keys": [
                      {
                        "type": "GlobalReference",
                        "value": "http://admin-shell.io/vdi/2770/1/0/StoredDocumentRepresentation/DigitalFile"
                      }
                    ]
                  },
                  "value": "https://ywheivlrppourvacbxkz.supabase.co/storage/v1/object/public/datasheets/reley%20socket/finder_40.52.9.024.000.pdf",
                  "contentType": "EMPTY",
                  "modelType": "File"
                },
                {
                  "category": "CONSTANT",
                  "idShort": "SetDate",
                  "semanticId": {
                    "type": "ExternalReference",
                    "keys": [
                      {
                        "type": "GlobalReference",
                        "value": "http://admin-shell.io/vdi/2770/1/0/LifeCycleStatus/SetDate"
                      }
                    ]
                  },
                  "valueType": "xs:string",
                  "value": "18.05.2025",
                  "modelType": "Property"
                },
                {
                  "category": "CONSTANT",
                  "idShort": "OrganizationName",
                  "semanticId": {
                    "type": "ExternalReference",
                    "keys": [
                      {
                        "type": "GlobalReference",
                        "value": "http://admin-shell.io/vdi/2770/1/0/Organization/OrganizationName"
                      }
                    ]
                  },
                  "valueType": "xs:string",
                  "value": "FINDER S.p.A. sole proprietorship",
                  "modelType": "Property"
                }
              ],
              "modelType": "SubmodelElementCollection"
            }
          ],
          "modelType": "SubmodelElementCollection"
        },
        {
          "category": "CONSTANT",
          "idShort": "WERMA 693.010.55 12VDC IP65",
          "semanticId": {
            "type": "ExternalReference",
            "keys": [
              {
                "type": "GlobalReference",
                "value": "http://admin-shell.io/vdi/2770/1/0/Document"
              }
            ]
          },
          "value": [
            {
              "category": "CONSTANT",
              "idShort": "DocumentId",
              "semanticId": {
                "type": "ExternalReference",
                "keys": [
                  {
                    "type": "GlobalReference",
                    "value": "http://admin-shell.io/vdi/2770/1/0/DocumentId/Id"
                  }
                ]
              },
              "valueType": "xs:string",
              "value": "693.010.55",
              "modelType": "Property"
            },
            {
              "category": "CONSTANT",
              "idShort": "ClassId",
              "semanticId": {
                "type": "ExternalReference",
                "keys": [
                  {
                    "type": "GlobalReference",
                    "value": "http://admin-shell.io/vdi/2770/1/0/DocumentClassification/ClassId"
                  }
                ]
              },
              "valueType": "xs:string",
              "value": "02-01",
              "modelType": "Property"
            },
            {
              "category": "CONSTANT",
              "idShort": "ClassName",
              "semanticId": {
                "type": "ExternalReference",
                "keys": [
                  {
                    "type": "GlobalReference",
                    "value": "http://admin-shell.io/vdi/2770/1/0/DocumentClassification/ClassName"
                  }
                ]
              },
              "valueType": "xs:string",
              "value": "Technical specifiction",
              "modelType": "Property"
            },
            {
              "category": "CONSTANT",
              "idShort": "ClassificationSystem",
              "semanticId": {
                "type": "ExternalReference",
                "keys": [
                  {
                    "type": "GlobalReference",
                    "value": "http://admin-shell.io/vdi/2770/1/0/DocumentClassification/ClassificationSystem"
                  }
                ]
              },
              "valueType": "xs:string",
              "value": "VDI2770:2018",
              "modelType": "Property"
            },
            {
              "category": "CONSTANT",
              "idShort": "DocumentVersion{0:00}",
              "semanticId": {
                "type": "ExternalReference",
                "keys": [
                  {
                    "type": "GlobalReference",
                    "value": "http://admin-shell.io/vdi/2770/1/0/DocumentVersion"
                  }
                ]
              },
              "value": [
                {
                  "category": "CONSTANT",
                  "idShort": "Title",
                  "semanticId": {
                    "type": "ExternalReference",
                    "keys": [
                      {
                        "type": "GlobalReference",
                        "value": "http://admin-shell.io/vdi/2770/1/0/Description/Title"
                      }
                    ]
                  },
                  "value": [
                    {
                      "language": "de",
                      "text": "693.010.55"
                    }
                  ],
                  "modelType": "MultiLanguageProperty"
                },
                {
                  "category": "CONSTANT",
                  "idShort": "DigitalFile{0:00}",
                  "semanticId": {
                    "type": "ExternalReference",
                    "keys": [
                      {
                        "type": "GlobalReference",
                        "value": "http://admin-shell.io/vdi/2770/1/0/StoredDocumentRepresentation/DigitalFile"
                      }
                    ]
                  },
                  "value": "https://ywheivlrppourvacbxkz.supabase.co/storage/v1/object/public/datasheets/standby%20light/WERMA_693.010.55_12VDC_IP65.pdf",
                  "contentType": "EMPTY",
                  "modelType": "File"
                },
                {
                  "category": "CONSTANT",
                  "idShort": "SetDate",
                  "semanticId": {
                    "type": "ExternalReference",
                    "keys": [
                      {
                        "type": "GlobalReference",
                        "value": "http://admin-shell.io/vdi/2770/1/0/LifeCycleStatus/SetDate"
                      }
                    ]
                  },
                  "valueType": "xs:string",
                  "value": "18.05.2025",
                  "modelType": "Property"
                },
                {
                  "category": "CONSTANT",
                  "idShort": "OrganizationName",
                  "semanticId": {
                    "type": "ExternalReference",
                    "keys": [
                      {
                        "type": "GlobalReference",
                        "value": "http://admin-shell.io/vdi/2770/1/0/Organization/OrganizationName"
                      }
                    ]
                  },
                  "valueType": "xs:string",
                  "value": "WERMA Signaltechnik GmbH \u002B Co.KG",
                  "modelType": "Property"
                }
              ],
              "modelType": "SubmodelElementCollection"
            }
          ],
          "modelType": "SubmodelElementCollection"
        },
        {
          "category": "CONSTANT",
          "idShort": "SICK AHM36B-BBQC012X12",
          "semanticId": {
            "type": "ExternalReference",
            "keys": [
              {
                "type": "GlobalReference",
                "value": "http://admin-shell.io/vdi/2770/1/0/Document"
              }
            ]
          },
          "value": [
            {
              "category": "CONSTANT",
              "idShort": "DocumentId",
              "semanticId": {
                "type": "ExternalReference",
                "keys": [
                  {
                    "type": "GlobalReference",
                    "value": "http://admin-shell.io/vdi/2770/1/0/DocumentId/Id"
                  }
                ]
              },
              "valueType": "xs:string",
              "value": "AHM36B-BBQC012X12",
              "modelType": "Property"
            },
            {
              "category": "CONSTANT",
              "idShort": "ClassId",
              "semanticId": {
                "type": "ExternalReference",
                "keys": [
                  {
                    "type": "GlobalReference",
                    "value": "http://admin-shell.io/vdi/2770/1/0/DocumentClassification/ClassId"
                  }
                ]
              },
              "valueType": "xs:string",
              "value": "02-01",
              "modelType": "Property"
            },
            {
              "category": "CONSTANT",
              "idShort": "ClassName",
              "semanticId": {
                "type": "ExternalReference",
                "keys": [
                  {
                    "type": "GlobalReference",
                    "value": "http://admin-shell.io/vdi/2770/1/0/DocumentClassification/ClassName"
                  }
                ]
              },
              "valueType": "xs:string",
              "value": "Technical specifiction",
              "modelType": "Property"
            },
            {
              "category": "CONSTANT",
              "idShort": "ClassificationSystem",
              "semanticId": {
                "type": "ExternalReference",
                "keys": [
                  {
                    "type": "GlobalReference",
                    "value": "http://admin-shell.io/vdi/2770/1/0/DocumentClassification/ClassificationSystem"
                  }
                ]
              },
              "valueType": "xs:string",
              "value": "VDI2770:2018",
              "modelType": "Property"
            },
            {
              "category": "CONSTANT",
              "idShort": "DocumentVersion{0:00}",
              "semanticId": {
                "type": "ExternalReference",
                "keys": [
                  {
                    "type": "GlobalReference",
                    "value": "http://admin-shell.io/vdi/2770/1/0/DocumentVersion"
                  }
                ]
              },
              "value": [
                {
                  "category": "CONSTANT",
                  "idShort": "Title",
                  "semanticId": {
                    "type": "ExternalReference",
                    "keys": [
                      {
                        "type": "GlobalReference",
                        "value": "http://admin-shell.io/vdi/2770/1/0/Description/Title"
                      }
                    ]
                  },
                  "value": [
                    {
                      "language": "de",
                      "text": "AHM36B-BBQC012X12"
                    }
                  ],
                  "modelType": "MultiLanguageProperty"
                },
                {
                  "category": "CONSTANT",
                  "idShort": "DigitalFile{0:00}",
                  "semanticId": {
                    "type": "ExternalReference",
                    "keys": [
                      {
                        "type": "GlobalReference",
                        "value": "http://admin-shell.io/vdi/2770/1/0/StoredDocumentRepresentation/DigitalFile"
                      }
                    ]
                  },
                  "value": "https://ywheivlrppourvacbxkz.supabase.co/storage/v1/object/public/datasheets/encoder/SICK_AHM36B-BBQC012X12.pdf",
                  "contentType": "EMPTY",
                  "modelType": "File"
                },
                {
                  "category": "CONSTANT",
                  "idShort": "SetDate",
                  "semanticId": {
                    "type": "ExternalReference",
                    "keys": [
                      {
                        "type": "GlobalReference",
                        "value": "http://admin-shell.io/vdi/2770/1/0/LifeCycleStatus/SetDate"
                      }
                    ]
                  },
                  "valueType": "xs:string",
                  "value": "18.05.2025",
                  "modelType": "Property"
                },
                {
                  "category": "CONSTANT",
                  "idShort": "OrganizationName",
                  "semanticId": {
                    "type": "ExternalReference",
                    "keys": [
                      {
                        "type": "GlobalReference",
                        "value": "http://admin-shell.io/vdi/2770/1/0/Organization/OrganizationName"
                      }
                    ]
                  },
                  "valueType": "xs:string",
                  "value": "SICK AG",
                  "modelType": "Property"
                }
              ],
              "modelType": "SubmodelElementCollection"
            }
          ],
          "modelType": "SubmodelElementCollection"
        },
        {
          "category": "CONSTANT",
          "idShort": "Littelfuse 218 5x20mm",
          "semanticId": {
            "type": "ExternalReference",
            "keys": [
              {
                "type": "GlobalReference",
                "value": "http://admin-shell.io/vdi/2770/1/0/Document"
              }
            ]
          },
          "value": [
            {
              "category": "CONSTANT",
              "idShort": "DocumentId",
              "semanticId": {
                "type": "ExternalReference",
                "keys": [
                  {
                    "type": "GlobalReference",
                    "value": "http://admin-shell.io/vdi/2770/1/0/DocumentId/Id"
                  }
                ]
              },
              "valueType": "xs:string",
              "value": "218",
              "modelType": "Property"
            },
            {
              "category": "CONSTANT",
              "idShort": "ClassId",
              "semanticId": {
                "type": "ExternalReference",
                "keys": [
                  {
                    "type": "GlobalReference",
                    "value": "http://admin-shell.io/vdi/2770/1/0/DocumentClassification/ClassId"
                  }
                ]
              },
              "valueType": "xs:string",
              "value": "02-01",
              "modelType": "Property"
            },
            {
              "category": "CONSTANT",
              "idShort": "ClassName",
              "semanticId": {
                "type": "ExternalReference",
                "keys": [
                  {
                    "type": "GlobalReference",
                    "value": "http://admin-shell.io/vdi/2770/1/0/DocumentClassification/ClassName"
                  }
                ]
              },
              "valueType": "xs:string",
              "value": "Technical specifiction",
              "modelType": "Property"
            },
            {
              "category": "CONSTANT",
              "idShort": "ClassificationSystem",
              "semanticId": {
                "type": "ExternalReference",
                "keys": [
                  {
                    "type": "GlobalReference",
                    "value": "http://admin-shell.io/vdi/2770/1/0/DocumentClassification/ClassificationSystem"
                  }
                ]
              },
              "valueType": "xs:string",
              "value": "VDI2770:2018",
              "modelType": "Property"
            },
            {
              "category": "CONSTANT",
              "idShort": "DocumentVersion{0:00}",
              "semanticId": {
                "type": "ExternalReference",
                "keys": [
                  {
                    "type": "GlobalReference",
                    "value": "http://admin-shell.io/vdi/2770/1/0/DocumentVersion"
                  }
                ]
              },
              "value": [
                {
                  "category": "CONSTANT",
                  "idShort": "Title",
                  "semanticId": {
                    "type": "ExternalReference",
                    "keys": [
                      {
                        "type": "GlobalReference",
                        "value": "http://admin-shell.io/vdi/2770/1/0/Description/Title"
                      }
                    ]
                  },
                  "value": [
                    {
                      "language": "de",
                      "text": "218"
                    }
                  ],
                  "modelType": "MultiLanguageProperty"
                },
                {
                  "category": "CONSTANT",
                  "idShort": "DigitalFile{0:00}",
                  "semanticId": {
                    "type": "ExternalReference",
                    "keys": [
                      {
                        "type": "GlobalReference",
                        "value": "http://admin-shell.io/vdi/2770/1/0/StoredDocumentRepresentation/DigitalFile"
                      }
                    ]
                  },
                  "value": "https://ywheivlrppourvacbxkz.supabase.co/storage/v1/object/public/datasheets/fuses/Littelfuse_218_5x20mm.pdf",
                  "contentType": "EMPTY",
                  "modelType": "File"
                },
                {
                  "category": "CONSTANT",
                  "idShort": "SetDate",
                  "semanticId": {
                    "type": "ExternalReference",
                    "keys": [
                      {
                        "type": "GlobalReference",
                        "value": "http://admin-shell.io/vdi/2770/1/0/LifeCycleStatus/SetDate"
                      }
                    ]
                  },
                  "valueType": "xs:string",
                  "value": "18.05.2025",
                  "modelType": "Property"
                },
                {
                  "category": "CONSTANT",
                  "idShort": "OrganizationName",
                  "semanticId": {
                    "type": "ExternalReference",
                    "keys": [
                      {
                        "type": "GlobalReference",
                        "value": "http://admin-shell.io/vdi/2770/1/0/Organization/OrganizationName"
                      }
                    ]
                  },
                  "valueType": "xs:string",
                  "value": "Littelfuse, Inc.",
                  "modelType": "Property"
                }
              ],
              "modelType": "SubmodelElementCollection"
            }
          ],
          "modelType": "SubmodelElementCollection"
        },
        {
          "category": "CONSTANT",
          "idShort": "Goobay Sicherungshalter GSH 135 5x20mm",
          "semanticId": {
            "type": "ExternalReference",
            "keys": [
              {
                "type": "GlobalReference",
                "value": "http://admin-shell.io/vdi/2770/1/0/Document"
              }
            ]
          },
          "value": [
            {
              "category": "CONSTANT",
              "idShort": "DocumentId",
              "semanticId": {
                "type": "ExternalReference",
                "keys": [
                  {
                    "type": "GlobalReference",
                    "value": "http://admin-shell.io/vdi/2770/1/0/DocumentId/Id"
                  }
                ]
              },
              "valueType": "xs:string",
              "value": "135",
              "modelType": "Property"
            },
            {
              "category": "CONSTANT",
              "idShort": "ClassId",
              "semanticId": {
                "type": "ExternalReference",
                "keys": [
                  {
                    "type": "GlobalReference",
                    "value": "http://admin-shell.io/vdi/2770/1/0/DocumentClassification/ClassId"
                  }
                ]
              },
              "valueType": "xs:string",
              "value": "02-01",
              "modelType": "Property"
            },
            {
              "category": "CONSTANT",
              "idShort": "ClassName",
              "semanticId": {
                "type": "ExternalReference",
                "keys": [
                  {
                    "type": "GlobalReference",
                    "value": "http://admin-shell.io/vdi/2770/1/0/DocumentClassification/ClassName"
                  }
                ]
              },
              "valueType": "xs:string",
              "value": "Technical specifiction",
              "modelType": "Property"
            },
            {
              "category": "CONSTANT",
              "idShort": "ClassificationSystem",
              "semanticId": {
                "type": "ExternalReference",
                "keys": [
                  {
                    "type": "GlobalReference",
                    "value": "http://admin-shell.io/vdi/2770/1/0/DocumentClassification/ClassificationSystem"
                  }
                ]
              },
              "valueType": "xs:string",
              "value": "VDI2770:2018",
              "modelType": "Property"
            },
            {
              "category": "CONSTANT",
              "idShort": "DocumentVersion{0:00}",
              "semanticId": {
                "type": "ExternalReference",
                "keys": [
                  {
                    "type": "GlobalReference",
                    "value": "http://admin-shell.io/vdi/2770/1/0/DocumentVersion"
                  }
                ]
              },
              "value": [
                {
                  "category": "CONSTANT",
                  "idShort": "Title",
                  "semanticId": {
                    "type": "ExternalReference",
                    "keys": [
                      {
                        "type": "GlobalReference",
                        "value": "http://admin-shell.io/vdi/2770/1/0/Description/Title"
                      }
                    ]
                  },
                  "value": [
                    {
                      "language": "de",
                      "text": "135"
                    }
                  ],
                  "modelType": "MultiLanguageProperty"
                },
                {
                  "category": "CONSTANT",
                  "idShort": "DigitalFile{0:00}",
                  "semanticId": {
                    "type": "ExternalReference",
                    "keys": [
                      {
                        "type": "GlobalReference",
                        "value": "http://admin-shell.io/vdi/2770/1/0/StoredDocumentRepresentation/DigitalFile"
                      }
                    ]
                  },
                  "value": "https://ywheivlrppourvacbxkz.supabase.co/storage/v1/object/public/datasheets/fuses/Goobay_Sicherungshalter_GSH_135_5x20mm.pdf",
                  "contentType": "EMPTY",
                  "modelType": "File"
                },
                {
                  "category": "CONSTANT",
                  "idShort": "SetDate",
                  "semanticId": {
                    "type": "ExternalReference",
                    "keys": [
                      {
                        "type": "GlobalReference",
                        "value": "http://admin-shell.io/vdi/2770/1/0/LifeCycleStatus/SetDate"
                      }
                    ]
                  },
                  "valueType": "xs:string",
                  "value": "18.05.2025",
                  "modelType": "Property"
                },
                {
                  "category": "CONSTANT",
                  "idShort": "OrganizationName",
                  "semanticId": {
                    "type": "ExternalReference",
                    "keys": [
                      {
                        "type": "GlobalReference",
                        "value": "http://admin-shell.io/vdi/2770/1/0/Organization/OrganizationName"
                      }
                    ]
                  },
                  "valueType": "xs:string",
                  "value": "Wentronic GmbH",
                  "modelType": "Property"
                }
              ],
              "modelType": "SubmodelElementCollection"
            }
          ],
          "modelType": "SubmodelElementCollection"
        }
      ],
      "modelType": "Submodel"
    },
    {
      "id": "https://admin-shell.io/idta/SubmodelTemplate/CarbonFootprint/0/9",
      "kind": "Template",
      "idShort": "CarbonFootprint",
      "modelType": "Submodel",
      "semanticId": {
        "keys": [
          {
            "type": "Submodel",
            "value": "https://admin-shell.io/idta/CarbonFootprint/CarbonFootprint/0/9"
          }
        ],
        "type": "ModelReference"
      },
      "description": [
        {
          "text": "The Submodel provides the means to access the Carbon Footprint …",
          "language": "en"
        }
      ],
      "displayName": [
        {
          "text": "C02 Footprint",
          "language": "de"
        },
        {
          "text": "Carbon Footprint",
          "language": "en"
        }
      ],
      "administration": {
        "version": "0",
        "revision": "9",
        "templateId": "https://admin-shell.io/idta/CarbonFootprint/CarbonFootprint/0/9"
      },
      "submodelElements": [
        {
            "idShort": "BauteilAdressen",
            "modelType": "SubmodelElementCollection",
            "value": [
              {
                "idShort": "BauteilAdressen",
                "modelType": "SubmodelElementCollection",
                "value": [
                  {
                    "idShort": "Bauteil_0",
                    "modelType": "SubmodelElementCollection",
                    "value": [
                          { "idShort": "Name",        "modelType": "Property", "valueType": "xs:string", "value": "FH Technikum Wien" },
                          { "idShort": "Street",      "modelType": "Property", "valueType": "xs:string", "value": "Höchstädtplatz" },
                          { "idShort": "HouseNumber", "modelType": "Property", "valueType": "xs:string", "value": "6" },
                          { "idShort": "ZipCode",     "modelType": "Property", "valueType": "xs:string", "value": "1200" },
                          { "idShort": "CityTown",    "modelType": "Property", "valueType": "xs:string", "value": "Wien" },
                          { "idShort": "Country",     "modelType": "Property", "valueType": "xs:string", "value": "Österreich" },
                          { "idShort": "Latitude",    "modelType": "Property", "valueType": "xs:double", "value": 48.23916732631421 },
                          { "idShort": "Longitude",   "modelType": "Property", "valueType": "xs:double", "value": 16.377420365898587 }
                        ]
                      },
                      {
                        "idShort": "Bauteil_micro_motors_E192-24-49",
                        "modelType": "SubmodelElementCollection",
                        "value": [
                          { "idShort": "Name",        "modelType": "Property", "valueType": "xs:string", "value": "micro motors E192-24-49" },
                          { "idShort": "Street",      "modelType": "Property", "valueType": "xs:string", "value": "Via Consorziale" },
                          { "idShort": "HouseNumber", "modelType": "Property", "valueType": "xs:string", "value": "13" },
                          { "idShort": "ZipCode",     "modelType": "Property", "valueType": "xs:string", "value": "33170" },
                          { "idShort": "CityTown",    "modelType": "Property", "valueType": "xs:string", "value": "Pordenone" },
                          { "idShort": "Country",     "modelType": "Property", "valueType": "xs:string", "value": "Italy" },
                          { "idShort": "Latitude",    "modelType": "Property", "valueType": "xs:double", "value": 45.982248916632265 },
                          { "idShort": "Longitude",   "modelType": "Property", "valueType": "xs:double", "value": 12.629289635055414 }
                        ]
                      },
                      {
                        "idShort": "Bauteil_micro_motors_E192.24.336",
                        "modelType": "SubmodelElementCollection",
                        "value": [
                          { "idShort": "Name",        "modelType": "Property", "valueType": "xs:string", "value": "micro motors E192.24.336" },
                          { "idShort": "Street",      "modelType": "Property", "valueType": "xs:string", "value": "Via Consorziale" },
                          { "idShort": "HouseNumber", "modelType": "Property", "valueType": "xs:string", "value": "13" },
                          { "idShort": "ZipCode",     "modelType": "Property", "valueType": "xs:string", "value": "33170" },
                          { "idShort": "CityTown",    "modelType": "Property", "valueType": "xs:string", "value": "Pordenone" },
                          { "idShort": "Country",     "modelType": "Property", "valueType": "xs:string", "value": "Italy" },
                          { "idShort": "Latitude",    "modelType": "Property", "valueType": "xs:double", "value": 45.982248916632265 },
                          { "idShort": "Longitude",   "modelType": "Property", "valueType": "xs:double", "value": 12.629289635055414 }
                        ]
                      },
                      {
                        "idShort": "Bauteil_SMC_LEY16B-100-S1CL18",
                        "modelType": "SubmodelElementCollection",
                        "value": [
                          { "idShort": "Name",        "modelType": "Property", "valueType": "xs:string", "value": "SMC LEY16B-100-S1CL18" },
                          { "idShort": "Street",      "modelType": "Property", "valueType": "xs:string", "value": "Onogomachi" },
                          { "idShort": "HouseNumber", "modelType": "Property", "valueType": "xs:string", "value": "6133" },
                          { "idShort": "ZipCode",     "modelType": "Property", "valueType": "xs:string", "value": "300-2521" },
                          { "idShort": "CityTown",    "modelType": "Property", "valueType": "xs:string", "value": "Joso, Ibaraki" },
                          { "idShort": "Country",     "modelType": "Property", "valueType": "xs:string", "value": "Japan" },
                          { "idShort": "Latitude",    "modelType": "Property", "valueType": "xs:double", "value": 36.08635988961443 },
                          { "idShort": "Longitude",   "modelType": "Property", "valueType": "xs:double", "value": 139.98265395953365 }
                        ]
                      },
                      {
                        "idShort": "Bauteil_SMC_LEYG16MB-100-S1CL18",
                        "modelType": "SubmodelElementCollection",
                        "value": [
                          { "idShort": "Name",        "modelType": "Property", "valueType": "xs:string", "value": "SMC LEYG16MB-100-S1CL18" },
                          { "idShort": "Street",      "modelType": "Property", "valueType": "xs:string", "value": "Onogomachi" },
                          { "idShort": "HouseNumber", "modelType": "Property", "valueType": "xs:string", "value": "6133" },
                          { "idShort": "ZipCode",     "modelType": "Property", "valueType": "xs:string", "value": "300-2521" },
                          { "idShort": "CityTown",    "modelType": "Property", "valueType": "xs:string", "value": "Joso, Ibaraki" },
                          { "idShort": "Country",     "modelType": "Property", "valueType": "xs:string", "value": "Japan" },
                          { "idShort": "Latitude",    "modelType": "Property", "valueType": "xs:double", "value": 36.08635988961443 },
                          { "idShort": "Longitude",   "modelType": "Property", "valueType": "xs:double", "value": 139.98265395953365 }
                        ]
                      },
                      {
                        "idShort": "Bauteil_Siemens_Simatic_S7-1200_CPU_1215C",
                        "modelType": "SubmodelElementCollection",
                        "value": [
                          { "idShort": "Name",        "modelType": "Property", "valueType": "xs:string", "value": "Siemens Simatic S7-1200 CPU 1215C" },
                          { "idShort": "Street",      "modelType": "Property", "valueType": "xs:string", "value": "Werner-von-Siemens-Straße" },
                          { "idShort": "HouseNumber", "modelType": "Property", "valueType": "xs:string", "value": "48-52" },
                          { "idShort": "ZipCode",     "modelType": "Property", "valueType": "xs:string", "value": "92224" },
                          { "idShort": "CityTown",    "modelType": "Property", "valueType": "xs:string", "value": "Amberg" },
                          { "idShort": "Country",     "modelType": "Property", "valueType": "xs:string", "value": "Deutschland" },
                          { "idShort": "Latitude",    "modelType": "Property", "valueType": "xs:double", "value": 49.43429196878909 },
                          { "idShort": "Longitude",   "modelType": "Property", "valueType": "xs:double", "value": 11.86592292003358 }
                        ]
                      },
                      {
                        "idShort": "Bauteil_SICK_SIG200-0A0412200",
                        "modelType": "SubmodelElementCollection",
                        "value": [
                          { "idShort": "Name",        "modelType": "Property", "valueType": "xs:string", "value": "SICK SIG200-0A0412200" },
                          { "idShort": "Street",      "modelType": "Property", "valueType": "xs:string", "value": "Gisela-Sick-Straße" },
                          { "idShort": "HouseNumber", "modelType": "Property", "valueType": "xs:string", "value": "1" },
                          { "idShort": "ZipCode",     "modelType": "Property", "valueType": "xs:string", "value": "79276" },
                          { "idShort": "CityTown",    "modelType": "Property", "valueType": "xs:string", "value": "Reute" },
                          { "idShort": "Country",     "modelType": "Property", "valueType": "xs:string", "value": "Deutschland" },
                          { "idShort": "Latitude",    "modelType": "Property", "valueType": "xs:double", "value": 48.08531544197908 },
                          { "idShort": "Longitude",   "modelType": "Property", "valueType": "xs:double", "value": 7.808078361916123 }
                        ]
                      },
                      {
                        "idShort": "Bauteil_SICK_SIM4000-0P03G10",
                        "modelType": "SubmodelElementCollection",
                        "value": [
                          { "idShort": "Name",        "modelType": "Property", "valueType": "xs:string", "value": "SICK SIM4000-0P03G10" },
                          { "idShort": "Street",      "modelType": "Property", "valueType": "xs:string", "value": "Gisela-Sick-Straße" },
                          { "idShort": "HouseNumber", "modelType": "Property", "valueType": "xs:string", "value": "1" },
                          { "idShort": "ZipCode",     "modelType": "Property", "valueType": "xs:string", "value": "79276" },
                          { "idShort": "CityTown",    "modelType": "Property", "valueType": "xs:string", "value": "Reute" },
                          { "idShort": "Country",     "modelType": "Property", "valueType": "xs:string", "value": "Deutschland" },
                          { "idShort": "Latitude",    "modelType": "Property", "valueType": "xs:double", "value": 48.08531544197908 },
                          { "idShort": "Longitude",   "modelType": "Property", "valueType": "xs:double", "value": 7.808078361916123 }
                        ]
                      },
                      {
                        "idShort": "Bauteil_SICK_WE4SC-3P2230S04",
                        "modelType": "SubmodelElementCollection",
                        "value": [
                          { "idShort": "Name",        "modelType": "Property", "valueType": "xs:string", "value": "SICK WE4SC-3P2230S04" },
                          { "idShort": "Street",      "modelType": "Property", "valueType": "xs:string", "value": "Gerbermatte" },
                          { "idShort": "HouseNumber", "modelType": "Property", "valueType": "xs:string", "value": "1" },
                          { "idShort": "ZipCode",     "modelType": "Property", "valueType": "xs:string", "value": "79183" },
                          { "idShort": "CityTown",    "modelType": "Property", "valueType": "xs:string", "value": "Waldkirch" },
                          { "idShort": "Country",     "modelType": "Property", "valueType": "xs:string", "value": "Deutschland" },
                          { "idShort": "Latitude",    "modelType": "Property", "valueType": "xs:double", "value": 48.08371960648209 },
                          { "idShort": "Longitude",   "modelType": "Property", "valueType": "xs:double", "value": 7.936504313580678 }
                        ]
                      },
                      {
                        "idShort": "Bauteil_Kemo_Power_Control_M171_16038DI",
                        "modelType": "SubmodelElementCollection",
                        "value": [
                          { "idShort": "Name",        "modelType": "Property", "valueType": "xs:string", "value": "Kemo Power Control M171 16038DI" },
                          { "idShort": "Street",      "modelType": "Property", "valueType": "xs:string", "value": "Leher Landstraße" },
                          { "idShort": "HouseNumber", "modelType": "Property", "valueType": "xs:string", "value": "20" },
                          { "idShort": "ZipCode",     "modelType": "Property", "valueType": "xs:string", "value": "27607" },
                          { "idShort": "CityTown",    "modelType": "Property", "valueType": "xs:string", "value": "Geestland-Langen" },
                          { "idShort": "Country",     "modelType": "Property", "valueType": "xs:string", "value": "Deutschland" },
                          { "idShort": "Latitude",    "modelType": "Property", "valueType": "xs:double", "value": 53.605638907268336 },
                          { "idShort": "Longitude",   "modelType": "Property", "valueType": "xs:double", "value": 8.59602482397401 }
                        ]
                      },
                      {
                        "idShort": "Bauteil_RND_315-00011",
                        "modelType": "SubmodelElementCollection",
                        "value": [
                          { "idShort": "Name",        "modelType": "Property", "valueType": "xs:string", "value": "RND 315-00011" },
                          { "idShort": "Street",      "modelType": "Property", "valueType": "xs:string", "value": "2 East Xintian Rd., Silicon Valley Dynamic Industry Zone, Building 2, 5/F" },
                          { "idShort": "HouseNumber", "modelType": "Property", "valueType": "xs:string", "value": "" },
                          { "idShort": "ZipCode",     "modelType": "Property", "valueType": "xs:string", "value": "518101" },
                          { "idShort": "CityTown",    "modelType": "Property", "valueType": "xs:string", "value": "Shenzhen, Bao-An District" },
                          { "idShort": "Country",     "modelType": "Property", "valueType": "xs:string", "value": "China" },
                          { "idShort": "Latitude",    "modelType": "Property", "valueType": "xs:double", "value": 22.75206038365994 },
                          { "idShort": "Longitude",   "modelType": "Property", "valueType": "xs:double", "value": 114.02457989019473 }
                        ]
                      },
                      {
                        "idShort": "Bauteil_SMC_JXCL18-LEY16B-100",
                        "modelType": "SubmodelElementCollection",
                        "value": [
                          { "idShort": "Name",        "modelType": "Property", "valueType": "xs:string", "value": "SMC JXCL18-LEY16B-100" },
                          { "idShort": "Street",      "modelType": "Property", "valueType": "xs:string", "value": "Onogomachi" },
                          { "idShort": "HouseNumber", "modelType": "Property", "valueType": "xs:string", "value": "6133" },
                          { "idShort": "ZipCode",     "modelType": "Property", "valueType": "xs:string", "value": "300-2521" },
                          { "idShort": "CityTown",    "modelType": "Property", "valueType": "xs:string", "value": "Joso, Ibaraki" },
                          { "idShort": "Country",     "modelType": "Property", "valueType": "xs:string", "value": "Japan" },
                          { "idShort": "Latitude",    "modelType": "Property", "valueType": "xs:double", "value": 36.08635988961443 },
                          { "idShort": "Longitude",   "modelType": "Property", "valueType": "xs:double", "value": 139.98265395953365 }
                        ]
                      },
                      {
                        "idShort": "Bauteil_TP-Link_TL-WR802N",
                        "modelType": "SubmodelElementCollection",
                        "value": [
                          { "idShort": "Name",        "modelType": "Property", "valueType": "xs:string", "value": "TP-Link TL-WR802N" },
                          { "idShort": "Street",      "modelType": "Property", "valueType": "xs:string", "value": "Yinhai Road, Songshan Lake Science & Technology Industrial Park" },
                          { "idShort": "HouseNumber", "modelType": "Property", "valueType": "xs:string", "value": "No. 3" },
                          { "idShort": "ZipCode",     "modelType": "Property", "valueType": "xs:string", "value": "523808" },
                          { "idShort": "CityTown",    "modelType": "Property", "valueType": "xs:string", "value": "Dalang Town, Dongguan, Guangdong" },
                          { "idShort": "Country",     "modelType": "Property", "valueType": "xs:string", "value": "China" },
                          { "idShort": "Latitude",    "modelType": "Property", "valueType": "xs:double", "value": 22.96506015878785 },
                          { "idShort": "Longitude",   "modelType": "Property", "valueType": "xs:double", "value": 113.8977005766047 }
                        ]
                      },
                      {
                        "idShort": "Bauteil_finder_95_95_3",
                        "modelType": "SubmodelElementCollection",
                        "value": [
                          { "idShort": "Name",        "modelType": "Property", "valueType": "xs:string", "value": "finder 95.95.3" },
                          { "idShort": "Street",      "modelType": "Property", "valueType": "xs:string", "value": "Via Drubiaglio" },
                          { "idShort": "HouseNumber", "modelType": "Property", "valueType": "xs:string", "value": "14" },
                          { "idShort": "ZipCode",     "modelType": "Property", "valueType": "xs:string", "value": "10040" },
                          { "idShort": "CityTown",    "modelType": "Property", "valueType": "xs:string", "value": "Almese" },
                          { "idShort": "Country",     "modelType": "Property", "valueType": "xs:string", "value": "Italy" },
                          { "idShort": "Latitude",    "modelType": "Property", "valueType": "xs:double", "value": 45.10492208739367 },
                          { "idShort": "Longitude",   "modelType": "Property", "valueType": "xs:double", "value": 7.419044587279091 }
                        ]
                      },
                      {
                        "idShort": "Bauteil_finder_40_52_9_024_000",
                        "modelType": "SubmodelElementCollection",
                        "value": [
                          { "idShort": "Name",        "modelType": "Property", "valueType": "xs:string", "value": "finder 40.52.9.024.000" },
                          { "idShort": "Street",      "modelType": "Property", "valueType": "xs:string", "value": "Via Drubiaglio" },
                          { "idShort": "HouseNumber", "modelType": "Property", "valueType": "xs:string", "value": "14" },
                          { "idShort": "ZipCode",     "modelType": "Property", "valueType": "xs:string", "value": "10040" },
                          { "idShort": "CityTown",    "modelType": "Property", "valueType": "xs:string", "value": "Almese" },
                          { "idShort": "Country",     "modelType": "Property", "valueType": "xs:string", "value": "Italy" },
                          { "idShort": "Latitude",    "modelType": "Property", "valueType": "xs:double", "value": 45.10492208739367 },
                          { "idShort": "Longitude",   "modelType": "Property", "valueType": "xs:double", "value": 7.419044587279091 }
                        ]
                      },
                      {
                        "idShort": "Bauteil_werma_693_010_55_12vdc_ip65",
                        "modelType": "SubmodelElementCollection",
                        "value": [
                          { "idShort": "Name",        "modelType": "Property", "valueType": "xs:string", "value": "WERMA 693.010.55 12VDC IP65" },
                          { "idShort": "Street",      "modelType": "Property", "valueType": "xs:string", "value": "Dürbheimer Str." },
                          { "idShort": "HouseNumber", "modelType": "Property", "valueType": "xs:string", "value": "15" },
                          { "idShort": "ZipCode",     "modelType": "Property", "valueType": "xs:string", "value": "78604" },
                          { "idShort": "CityTown",    "modelType": "Property", "valueType": "xs:string", "value": "Rietheim-Weilheim" },
                          { "idShort": "Country",     "modelType": "Property", "valueType": "xs:string", "value": "Deutschland" },
                          { "idShort": "Latitude",    "modelType": "Property", "valueType": "xs:double", "value": 48.03690510457408 },
                          { "idShort": "Longitude",   "modelType": "Property", "valueType": "xs:double", "value": 8.777752280134374 }
                        ]
                      },
                      {
                        "idShort": "Bauteil_sick_ahm36b_bbqc012x12",
                        "modelType": "SubmodelElementCollection",
                        "value": [
                          { "idShort": "Name",        "modelType": "Property", "valueType": "xs:string", "value": "SICK AHM36B-BBQC012X12" },
                          { "idShort": "Street",      "modelType": "Property", "valueType": "xs:string", "value": "Dürrheimer Str." },
                          { "idShort": "HouseNumber", "modelType": "Property", "valueType": "xs:string", "value": "36" },
                          { "idShort": "ZipCode",     "modelType": "Property", "valueType": "xs:string", "value": "78166" },
                          { "idShort": "CityTown",    "modelType": "Property", "valueType": "xs:string", "value": "Donaueschingen" },
                          { "idShort": "Country",     "modelType": "Property", "valueType": "xs:string", "value": "Deutschland" },
                          { "idShort": "Latitude",    "modelType": "Property", "valueType": "xs:double", "value": 47.96008728337855 },
                          { "idShort": "Longitude",   "modelType": "Property", "valueType": "xs:double", "value": 8.504355509220776 }
                        ]
                      },
                      {
                        "idShort": "Bauteil_littelfuse_218_5x20mm",
                        "modelType": "SubmodelElementCollection",
                        "value": [
                          { "idShort": "Name",        "modelType": "Property", "valueType": "xs:string", "value": "Littelfuse 218 5x20mm" },
                          { "idShort": "Street",      "modelType": "Property", "valueType": "xs:string", "value": "Lima Technology Center, Special Economic Zone, Malvar" },
                          { "idShort": "HouseNumber", "modelType": "Property", "valueType": "xs:string", "value": "" },
                          { "idShort": "ZipCode",     "modelType": "Property", "valueType": "xs:string", "value": "4217" },
                          { "idShort": "CityTown",    "modelType": "Property", "valueType": "xs:string", "value": "Lipa City, Batangas" },
                          { "idShort": "Country",     "modelType": "Property", "valueType": "xs:string", "value": "Philippinen" },
                          { "idShort": "Latitude",    "modelType": "Property", "valueType": "xs:double", "value": 13.946507127228643 },
                          { "idShort": "Longitude",   "modelType": "Property", "valueType": "xs:double", "value": 121.16315525021904 }
                        ]
                      },
                      {
                        "idShort": "Bauteil_goobay_gsh_135_5x20mm",
                        "modelType": "SubmodelElementCollection",
                        "value": [
                          { "idShort": "Name",        "modelType": "Property", "valueType": "xs:string", "value": "Goobay Sicherungshalter GSH 135 5x20mm" },
                          { "idShort": "Street",      "modelType": "Property", "valueType": "xs:string", "value": "East Street, Caiwu 4. Industriepark, Gemeinde Wusha, Zhen’an Straße, Stadtteil Chang’an" },
                          { "idShort": "HouseNumber", "modelType": "Property", "valueType": "xs:string", "value": "5" },
                          { "idShort": "ZipCode",     "modelType": "Property", "valueType": "xs:string", "value": "523860" },
                          { "idShort": "CityTown",    "modelType": "Property", "valueType": "xs:string", "value": "Dongguan, Provinz Guangdong" },
                          { "idShort": "Country",     "modelType": "Property", "valueType": "xs:string", "value": "China" },
                          { "idShort": "Latitude",    "modelType": "Property", "valueType": "xs:double", "value": 22.79769555918711 },
                          { "idShort": "Longitude",   "modelType": "Property", "valueType": "xs:double", "value": 113.8142370329572 }
                        ]
                      }
                    ]
                  }
                ]
              },
              {
                "idShort": "CFPhases",
                "modelType": "Property",
                "value": {
                  "phases": {
                    "A1": 258.59,
                    "A2": 2.31,
                    "A3": 3.50,
                    "A4": 0.00
                  }
                }
              },             
        {
          "value": [
            {
              "idShort": "PCFCalculationMethod",
              "category": "PARAMETER",
              "modelType": "Property",
              "valueType": "xs:string",
              "qualifiers": [
                {
                  "kind": "ConceptQualifier",
                  "type": "Cardinality",
                  "value": "OneToMany",
                  "valueType": "xs:string"
                }
              ],
              "semanticId": {
                "keys": [
                  {
                    "type": "GlobalReference",
                    "value": "0173-1#02-ABG854#001"
                  }
                ],
                "type": "ExternalReference"
              },
              "description": [
                {
                  "text": "Standard, method for determining the greenhouse gas emissions of a product",
                  "language": "en"
                },
                {
                  "text": "Norm, Standard, Verfahren zur Ermittlung der Treibhausgas-Emissionen eines Produkts",
                  "language": "de"
                }
              ],
              "displayName": [
                {
                  "text": "Folgenabschätzungsmethode / Berechnungsmethode",
                  "language": "de"
                },
                {
                  "text": "impact assessment method / calculation method",
                  "language": "en"
                }
              ]
            },
            {
              "idShort": "PCFCO2eq",
              "category": "PARAMETER",
              "modelType": "Property",
              "valueType": "xs:double",
              "qualifiers": [
                {
                  "kind": "ConceptQualifier",
                  "type": "Cardinality",
                  "value": "One",
                  "valueType": "xs:string"
                }
              ],
              "semanticId": {
                "keys": [
                  {
                    "type": "GlobalReference",
                    "value": "0173-1#02-ABG855#001"
                  }
                ],
                "type": "ExternalReference"
              },
              "description": [
                {
                  "text": "Sum of all greenhouse gas emissions of a product according to the quantification requirements of the standard",
                  "language": "en"
                }
              ],
              "displayName": [
                {
                  "text": "CO2 eq Klimawandel",
                  "language": "de"
                },
                {
                  "text": "CO2 eq Climate Change",
                  "language": "en"
                }
              ]
            },
            {
              "idShort": "PCFReferenceValueForCalculation",
              "category": "PARAMETER",
              "modelType": "Property",
              "valueType": "xs:string",
              "qualifiers": [
                {
                  "kind": "ConceptQualifier",
                  "type": "Cardinality",
                  "value": "One",
                  "valueType": "xs:string"
                }
              ],
              "semanticId": {
                "keys": [
                  {
                    "type": "GlobalReference",
                    "value": "0173-1#02-ABG856#001"
                  }
                ],
                "type": "ExternalReference"
              },
              "description": [
                {
                  "text": "Quantity unit of the product to which the PCF information on the CO2 footprint refers",
                  "language": "en"
                }
              ],
              "displayName": [
                {
                  "text": "Referenzeinheit für die Berechnung",
                  "language": "de"
                },
                {
                  "text": "Reference value for calculation",
                  "language": "en"
                }
              ]
            },
            {
              "idShort": "PCFQuantityOfMeasureForCalculation",
              "category": "PARAMETER",
              "modelType": "Property",
              "valueType": "xs:double",
              "qualifiers": [
                {
                  "kind": "ConceptQualifier",
                  "type": "Cardinality",
                  "value": "One",
                  "valueType": "xs:string"
                }
              ],
              "semanticId": {
                "keys": [
                  {
                    "type": "GlobalReference",
                    "value": "0173-1#02-ABG857#001"
                  }
                ],
                "type": "ExternalReference"
              },
              "description": [
                {
                  "text": "Quantity of the product to which the PCF information on the CO2 footprint refers",
                  "language": "en"
                }
              ],
              "displayName": [
                {
                  "text": "Mengenangabe für die Berechnung",
                  "language": "de"
                },
                {
                  "text": "quantity of measure for calculation",
                  "language": "en"
                }
              ]
            },
            {
              "idShort": "PCFLifeCyclePhase",
              "category": "PARAMETER",
              "modelType": "Property",
              "valueType": "xs:string",
              "qualifiers": [
                {
                  "kind": "ConceptQualifier",
                  "type": "Cardinality",
                  "value": "OneToMany",
                  "valueType": "xs:string"
                }
              ],
              "semanticId": {
                "keys": [
                  {
                    "type": "GlobalReference",
                    "value": "0173-1#02-ABG858#001"
                  }
                ],
                "type": "ExternalReference"
              },
              "description": [
                {
                  "text": "Life cycle stages of the product according to the quantification requirements of the standard to which the PCF carbon footprint statement refers",
                  "language": "en"
                }
              ],
              "displayName": [
                {
                  "text": "Lebenszyklusphase",
                  "language": "de"
                },
                {
                  "text": "life cycle phase",
                  "language": "en"
                }
              ]
            },
            {
              "idShort": "ExplanatoryStatement",
              "category": "PARAMETER",
              "modelType": "File",
              "qualifiers": [
                {
                  "kind": "ConceptQualifier",
                  "type": "Cardinality",
                  "value": "ZeroToOne",
                  "valueType": "xs:string"
                }
              ],
              "semanticId": {
                "keys": [
                  {
                    "type": "GlobalReference",
                    "value": "https://admin-shell.io/idta/CarbonFootprint/ExplanatoryStatement/1/0"
                  }
                ],
                "type": "ExternalReference"
              },
              "contentType": "application/pdf",
              "description": [
                {
                  "text": "Explanation which is needed or given so that a footprint communication can be properly understood by a purchaser, potential purchaser or user of the product",
                  "language": "en"
                }
              ],
              "displayName": [
                {
                  "text": "Erklärung",
                  "language": "de"
                },
                {
                  "text": "Explanatory statement",
                  "language": "en"
                }
              ]
            },
            {
              "value": [
                {
                  "idShort": "Street",
                  "category": "PARAMETER",
                  "modelType": "Property",
                  "valueType": "xs:string",
                  "qualifiers": [
                    {
                      "kind": "ConceptQualifier",
                      "type": "Cardinality",
                      "value": "ZeroToOne",
                      "valueType": "xs:string"
                    }
                  ],
                  "semanticId": {
                    "keys": [
                      {
                        "type": "GlobalReference",
                        "value": "0173-1#02-ABH956#001"
                      }
                    ],
                    "type": "ExternalReference"
                  },
                  "description": [
                    {
                      "text": "Street indication of the place of transfer of goods",
                      "language": "en"
                    }
                  ]
                },
                {
                  "idShort": "HouseNumber",
                  "category": "PARAMETER",
                  "modelType": "Property",
                  "valueType": "xs:string",
                  "qualifiers": [
                    {
                      "kind": "ConceptQualifier",
                      "type": "Cardinality",
                      "value": "ZeroToOne",
                      "valueType": "xs:string"
                    }
                  ],
                  "semanticId": {
                    "keys": [
                      {
                        "type": "GlobalReference",
                        "value": "0173-1#02-ABH957#001"
                      }
                    ],
                    "type": "ExternalReference"
                  },
                  "description": [
                    {
                      "text": "Number for identification or differentiation of individual houses of a street",
                      "language": "en"
                    }
                  ]
                },
                {
                  "idShort": "ZipCode",
                  "category": "PARAMETER",
                  "modelType": "Property",
                  "valueType": "xs:string",
                  "qualifiers": [
                    {
                      "kind": "ConceptQualifier",
                      "type": "Cardinality",
                      "value": "ZeroToOne",
                      "valueType": "xs:string"
                    }
                  ],
                  "semanticId": {
                    "keys": [
                      {
                        "type": "GlobalReference",
                        "value": "0173-1#02-ABH958#001"
                      }
                    ],
                    "type": "ExternalReference"
                  },
                  "description": [
                    {
                      "text": "Zip code of the goods transfer address",
                      "language": "en"
                    }
                  ]
                },
                {
                  "idShort": "CityTown",
                  "category": "PARAMETER",
                  "modelType": "Property",
                  "valueType": "xs:string",
                  "qualifiers": [
                    {
                      "kind": "ConceptQualifier",
                      "type": "Cardinality",
                      "value": "ZeroToOne",
                      "valueType": "xs:string"
                    }
                  ],
                  "semanticId": {
                    "keys": [
                      {
                        "type": "GlobalReference",
                        "value": "0173-1#02-ABH959#001"
                      }
                    ],
                    "type": "ExternalReference"
                  },
                  "description": [
                    {
                      "text": "Indication of the city or town of the transfer of goods",
                      "language": "en"
                    }
                  ]
                },
                {
                  "idShort": "Country",
                  "category": "PARAMETER",
                  "modelType": "Property",
                  "valueType": "xs:string",
                  "qualifiers": [
                    {
                      "kind": "ConceptQualifier",
                      "type": "Cardinality",
                      "value": "ZeroToOne",
                      "valueType": "xs:string"
                    }
                  ],
                  "semanticId": {
                    "keys": [
                      {
                        "type": "GlobalReference",
                        "value": "0173-1#02-AAO259#005"
                      }
                    ],
                    "type": "ExternalReference"
                  },
                  "description": [
                    {
                      "text": "Country where the product is transmitted",
                      "language": "en"
                    }
                  ]
                }
              ],
              "idShort": "PCFGoodsAddressHandover",
              "modelType": "SubmodelElementCollection",
              "qualifiers": [
                {
                  "kind": "ConceptQualifier",
                  "type": "Cardinality",
                  "value": "One",
                  "valueType": "xs:string"
                }
              ],
              "semanticId": {
                "keys": [
                  {
                    "type": "GlobalReference",
                    "value": "0173-1#02-ABI497#001"
                  }
                ],
                "type": "ExternalReference"
              },
              "description": [
                {
                  "text": "Indicates the place of hand-over of the goods",
                  "language": "en"
                }
              ],
              "displayName": [
                {
                  "text": "PCF Warenübergabeadresse",
                  "language": "de"
                },
                {
                  "text": "PCF goods address hand-over",
                  "language": "en"
                }
              ]
            },
            {
              "idShort": "PublicationDate",
              "category": "PARAMETER",
              "modelType": "Property",
              "valueType": "xs:string",
              "qualifiers": [
                {
                  "kind": "ConceptQualifier",
                  "type": "Cardinality",
                  "value": "One",
                  "valueType": "xs:string"
                }
              ],
              "semanticId": {
                "keys": [
                  {
                    "type": "GlobalReference",
                    "value": "https://admin-shell.io/idta/CarbonFootprint/PublicationDate/1/0"
                  }
                ],
                "type": "ExternalReference"
              },
              "description": [
                {
                  "text": "Time at which something was first published or made available",
                  "language": "en"
                }
              ],
              "displayName": [
                {
                  "text": "Veröffentlichungsdatum",
                  "language": "de"
                },
                {
                  "text": "Publication date",
                  "language": "en"
                }
              ]
            },
            {
              "idShort": "ExpirationDate",
              "category": "PARAMETER",
              "modelType": "Property",
              "valueType": "xs:string",
              "qualifiers": [
                {
                  "kind": "ConceptQualifier",
                  "type": "Cardinality",
                  "value": "ZeroToOne",
                  "valueType": "xs:string"
                }
              ],
              "semanticId": {
                "keys": [
                  {
                    "type": "GlobalReference",
                    "value": "https://admin-shell.io/idta/CarbonFootprint/ExpirationnDate/1/0"
                  }
                ],
                "type": "ExternalReference"
              },
              "description": [
                {
                  "text": "Time at which something should no longer be used effectively because it may lose its validity, quality or safety",
                  "language": "en"
                }
              ],
              "displayName": [
                {
                  "text": "Ablaufdatum",
                  "language": "de"
                },
                {
                  "text": "Expiration date",
                  "language": "en"
                }
              ]
            }
          ],
          "idShort": "ProductCarbonFootprint",
          "modelType": "SubmodelElementCollection",
          "qualifiers": [
            {
              "kind": "ConceptQualifier",
              "type": "Cardinality",
              "value": "ZeroToMany",
              "valueType": "xs:string"
            }
          ],
          "semanticId": {
            "keys": [
              {
                "type": "GlobalReference",
                "value": "https://admin-shell.io/idta/CarbonFootprint/ProductCarbonFootprint/0/9"
              }
            ],
            "type": "ExternalReference"
          },
          "description": [
            {
              "text": "Balance of greenhouse gas emissions along the entire life cycle of a product in a defined application and in relation to a defined unit of use",
              "language": "en"
            }
          ],
          "displayName": [
            {
              "text": "Produkt C02-Fußabdruck",
              "language": "de"
            },
            {
              "text": "Product carbon footprint",
              "language": "en"
            }
          ]
        },
        {
          "value": [
            {
              "idShort": "TCFCalculationMethod",
              "category": "PARAMETER",
              "modelType": "Property",
              "valueType": "xs:string",
              "qualifiers": [
                {
                  "kind": "ConceptQualifier",
                  "type": "Cardinality",
                  "value": "One",
                  "valueType": "xs:string"
                }
              ],
              "semanticId": {
                "keys": [
                  {
                    "type": "GlobalReference",
                    "value": "0173-1#02-ABG859#001"
                  }
                ],
                "type": "ExternalReference"
              },
              "description": [
                {
                  "text": "Standard, method for determining the greenhouse gas emissions for the transport of a product",
                  "language": "en"
                }
              ],
              "displayName": [
                {
                  "text": "TCF Berechnungsmethode",
                  "language": "de"
                },
                {
                  "text": "TCF calculation method",
                  "language": "en"
                }
              ]
            },
            {
              "idShort": "TCFCO2eq",
              "category": "PARAMETER",
              "modelType": "Property",
              "valueType": "xs:double",
              "qualifiers": [
                {
                  "kind": "ConceptQualifier",
                  "type": "Cardinality",
                  "value": "One",
                  "valueType": "xs:string"
                }
              ],
              "semanticId": {
                "keys": [
                  {
                    "type": "GlobalReference",
                    "value": "0173-1#02-ABG860#001"
                  }
                ],
                "type": "ExternalReference"
              },
              "description": [
                {
                  "text": "Sum of all greenhouse gas emissions from vehicle operation",
                  "language": "en"
                }
              ],
              "displayName": [
                {
                  "text": "TCF CO2eq",
                  "language": "de"
                },
                {
                  "text": "TCF CO2eq",
                  "language": "en"
                }
              ]
            },
            {
              "idShort": "TCFReferenceValueForCalculation",
              "category": "PARAMETER",
              "modelType": "Property",
              "valueType": "xs:string",
              "qualifiers": [
                {
                  "kind": "ConceptQualifier",
                  "type": "Cardinality",
                  "value": "One",
                  "valueType": "xs:string"
                }
              ],
              "semanticId": {
                "keys": [
                  {
                    "type": "GlobalReference",
                    "value": "0173-1#02-ABG861#001"
                  }
                ],
                "type": "ExternalReference"
              },
              "description": [
                {
                  "text": "Amount of product to which the TCF carbon footprint statement relates",
                  "language": "en"
                }
              ],
              "displayName": [
                {
                  "text": "TCF Bezugsgröße für die Berechnung",
                  "language": "de"
                },
                {
                  "text": "TCF reference value for calculation",
                  "language": "en"
                }
              ]
            },
            {
              "idShort": "TCFQuantityOfMeasureForCalculation",
              "category": "PARAMETER",
              "modelType": "Property",
              "valueType": "xs:double",
              "qualifiers": [
                {
                  "kind": "ConceptQualifier",
                  "type": "Cardinality",
                  "value": "One",
                  "valueType": "xs:string"
                }
              ],
              "semanticId": {
                "keys": [
                  {
                    "type": "GlobalReference",
                    "value": "0173-1#02-ABG862#001"
                  }
                ],
                "type": "ExternalReference"
              },
              "description": [
                {
                  "text": "Quantity of the product to which the TCF information on the CO2 footprint refers",
                  "language": "en"
                }
              ],
              "displayName": [
                {
                  "text": "TCF Mengenangabe für die Berechnung",
                  "language": "de"
                },
                {
                  "text": "TCF quantity of measure for calculation",
                  "language": "en"
                }
              ]
            },
            {
              "idShort": "TCFProcessesForGreenhouseGasEmissionInATransportService",
              "category": "PARAMETER",
              "modelType": "Property",
              "valueType": "xs:string",
              "qualifiers": [
                {
                  "kind": "ConceptQualifier",
                  "type": "Cardinality",
                  "value": "OneToMany",
                  "valueType": "xs:string"
                }
              ],
              "semanticId": {
                "keys": [
                  {
                    "type": "GlobalReference",
                    "value": "0173-1#02-ABG863#001"
                  }
                ],
                "type": "ExternalReference"
              },
              "description": [
                {
                  "text": "Processes in a transport service to determine the sum of all direct or indirect greenhouse gas emissions from fuel supply and vehicle operation",
                  "language": "en"
                }
              ],
              "displayName": [
                {
                  "text": "TCF Prozesse für Treibhausgas-Emissionen bei Transportdiensten",
                  "language": "de"
                },
                {
                  "text": "TCF processes for greenhouse gas emissions in a transport servi…",
                  "language": "en"
                }
              ]
            },
            {
              "idShort": "ExplanatoryStatement",
              "category": "PARAMETER",
              "modelType": "File",
              "qualifiers": [
                {
                  "kind": "ConceptQualifier",
                  "type": "Cardinality",
                  "value": "ZeroToOne",
                  "valueType": "xs:string"
                }
              ],
              "semanticId": {
                "keys": [
                  {
                    "type": "GlobalReference",
                    "value": "https://example.com/ids/cd/3291_7022_2032_0718"
                  }
                ],
                "type": "ExternalReference"
              },
              "contentType": "application/pdf",
              "description": [
                {
                  "text": "Explanation which is needed or given so that a footprint communication can be properly understood by a purchaser, potential purchaser or user of the product",
                  "language": "en"
                }
              ],
              "displayName": [
                {
                  "text": "Erklärung",
                  "language": "de"
                },
                {
                  "text": "Explanatory statement",
                  "language": "en"
                }
              ]
            },
            {
              "value": [
                {
                  "idShort": "Street",
                  "category": "PARAMETER",
                  "modelType": "Property",
                  "valueType": "xs:string",
                  "qualifiers": [
                    {
                      "kind": "ConceptQualifier",
                      "type": "Cardinality",
                      "value": "ZeroToOne",
                      "valueType": "xs:string"
                    }
                  ],
                  "semanticId": {
                    "keys": [
                      {
                        "type": "GlobalReference",
                        "value": "0173-1#02-ABH956#001"
                      }
                    ],
                    "type": "ExternalReference"
                  },
                  "description": [
                    {
                      "text": "Street indication of the place of transfer of goods",
                      "language": "en"
                    }
                  ],
                  "displayName": [
                    {
                      "text": "Straße",
                      "language": "de"
                    },
                    {
                      "text": "street",
                      "language": "en"
                    }
                  ]
                },
                {
                  "idShort": "HouseNumber",
                  "category": "PARAMETER",
                  "modelType": "Property",
                  "valueType": "xs:string",
                  "qualifiers": [
                    {
                      "kind": "ConceptQualifier",
                      "type": "Cardinality",
                      "value": "ZeroToOne",
                      "valueType": "xs:string"
                    }
                  ],
                  "semanticId": {
                    "keys": [
                      {
                        "type": "GlobalReference",
                        "value": "0173-1#02-ABH957#001"
                      }
                    ],
                    "type": "ExternalReference"
                  },
                  "description": [
                    {
                      "text": "Street indication of the place of transfer of goods",
                      "language": "en"
                    }
                  ],
                  "displayName": [
                    {
                      "text": "Hausnummer",
                      "language": "de"
                    },
                    {
                      "text": "house number",
                      "language": "en"
                    }
                  ]
                },
                {
                  "idShort": "ZipCode",
                  "category": "PARAMETER",
                  "modelType": "Property",
                  "valueType": "xs:string",
                  "qualifiers": [
                    {
                      "kind": "ConceptQualifier",
                      "type": "Cardinality",
                      "value": "ZeroToOne",
                      "valueType": "xs:string"
                    }
                  ],
                  "semanticId": {
                    "keys": [
                      {
                        "type": "GlobalReference",
                        "value": "0173-1#02-ABH958#001"
                      }
                    ],
                    "type": "ExternalReference"
                  },
                  "description": [
                    {
                      "text": "Zip code of the goods transfer address",
                      "language": "en"
                    }
                  ],
                  "displayName": [
                    {
                      "text": "Postleitzahl",
                      "language": "de"
                    },
                    {
                      "text": "zip code",
                      "language": "en"
                    }
                  ]
                },
                {
                  "idShort": "CityTown",
                  "category": "PARAMETER",
                  "modelType": "Property",
                  "valueType": "xs:string",
                  "qualifiers": [
                    {
                      "kind": "ConceptQualifier",
                      "type": "Cardinality",
                      "value": "ZeroToOne",
                      "valueType": "xs:string"
                    }
                  ],
                  "semanticId": {
                    "keys": [
                      {
                        "type": "GlobalReference",
                        "value": "0173-1#02-ABH959#001"
                      }
                    ],
                    "type": "ExternalReference"
                  },
                  "description": [
                    {
                      "text": "Indication of the city or town of the transfer of goods",
                      "language": "en"
                    }
                  ],
                  "displayName": [
                    {
                      "text": "Ort",
                      "language": "de"
                    },
                    {
                      "text": "city, town",
                      "language": "en"
                    }
                  ]
                },
                {
                  "idShort": "Country",
                  "category": "PARAMETER",
                  "modelType": "Property",
                  "valueType": "xs:string",
                  "qualifiers": [
                    {
                      "kind": "ConceptQualifier",
                      "type": "Cardinality",
                      "value": "ZeroToOne",
                      "valueType": "xs:string"
                    }
                  ],
                  "semanticId": {
                    "keys": [
                      {
                        "type": "GlobalReference",
                        "value": "0173-1#02-AAO259#005"
                      }
                    ],
                    "type": "ExternalReference"
                  },
                  "description": [
                    {
                      "text": "Country where the product is transmitted",
                      "language": "en"
                    }
                  ],
                  "displayName": [
                    {
                      "text": "Land",
                      "language": "de"
                    },
                    {
                      "text": "Country",
                      "language": "en"
                    }
                  ]
                }
              ],
              "idShort": "TCFGoodsTransportAddressTakeover",
              "modelType": "SubmodelElementCollection",
              "qualifiers": [
                {
                  "kind": "ConceptQualifier",
                  "type": "Cardinality",
                  "value": "One",
                  "valueType": "xs:string"
                }
              ],
              "semanticId": {
                "keys": [
                  {
                    "type": "GlobalReference",
                    "value": "0173-1#02-ABI499#001"
                  }
                ],
                "type": "ExternalReference"
              },
              "description": [
                {
                  "text": "Indication of the place of receipt of goods ",
                  "language": "en"
                }
              ],
              "displayName": [
                {
                  "text": "Warenübernahmeadresse für die Distributionsstufe",
                  "language": "de"
                },
                {
                  "text": "Goods transport address take-over for distribution stage",
                  "language": "en"
                }
              ]
            },
            {
              "value": [
                {
                  "idShort": "Street",
                  "category": "PARAMETER",
                  "modelType": "Property",
                  "valueType": "xs:string",
                  "qualifiers": [
                    {
                      "kind": "ConceptQualifier",
                      "type": "Cardinality",
                      "value": "ZeroToOne",
                      "valueType": "xs:string"
                    }
                  ],
                  "semanticId": {
                    "keys": [
                      {
                        "type": "GlobalReference",
                        "value": "0173-1#02-ABH956#001"
                      }
                    ],
                    "type": "ExternalReference"
                  },
                  "description": [
                    {
                      "text": "Street indication of the place of transfer of goods",
                      "language": "en"
                    }
                  ]
                },
                {
                  "idShort": "HouseNumber",
                  "category": "PARAMETER",
                  "modelType": "Property",
                  "valueType": "xs:string",
                  "qualifiers": [
                    {
                      "kind": "ConceptQualifier",
                      "type": "Cardinality",
                      "value": "ZeroToOne",
                      "valueType": "xs:string"
                    }
                  ],
                  "semanticId": {
                    "keys": [
                      {
                        "type": "GlobalReference",
                        "value": "0173-1#02-ABH957#001"
                      }
                    ],
                    "type": "ExternalReference"
                  },
                  "description": [
                    {
                      "text": "Number for identification or differentiation of individual houses of a street",
                      "language": "en"
                    }
                  ]
                },
                {
                  "idShort": "ZipCode",
                  "category": "PARAMETER",
                  "modelType": "Property",
                  "valueType": "xs:string",
                  "qualifiers": [
                    {
                      "kind": "ConceptQualifier",
                      "type": "Cardinality",
                      "value": "ZeroToOne",
                      "valueType": "xs:string"
                    }
                  ],
                  "semanticId": {
                    "keys": [
                      {
                        "type": "GlobalReference",
                        "value": "0173-1#02-ABH958#001"
                      }
                    ],
                    "type": "ExternalReference"
                  },
                  "description": [
                    {
                      "text": "Zip code of the goods transfer address",
                      "language": "en"
                    }
                  ]
                },
                {
                  "idShort": "CityTown",
                  "category": "PARAMETER",
                  "modelType": "Property",
                  "valueType": "xs:string",
                  "qualifiers": [
                    {
                      "kind": "ConceptQualifier",
                      "type": "Cardinality",
                      "value": "ZeroToOne",
                      "valueType": "xs:string"
                    }
                  ],
                  "semanticId": {
                    "keys": [
                      {
                        "type": "GlobalReference",
                        "value": "0173-1#02-ABH959#001"
                      }
                    ],
                    "type": "ExternalReference"
                  },
                  "description": [
                    {
                      "text": "Indication of the city or town of the transfer of goods",
                      "language": "en"
                    }
                  ]
                },
                {
                  "idShort": "Country",
                  "category": "PARAMETER",
                  "modelType": "Property",
                  "valueType": "xs:string",
                  "qualifiers": [
                    {
                      "kind": "ConceptQualifier",
                      "type": "Cardinality",
                      "value": "ZeroToOne",
                      "valueType": "xs:string"
                    }
                  ],
                  "semanticId": {
                    "keys": [
                      {
                        "type": "GlobalReference",
                        "value": "0173-1#02-AAO259#005"
                      }
                    ],
                    "type": "ExternalReference"
                  },
                  "description": [
                    {
                      "text": "Country where the product is transmitted",
                      "language": "en"
                    }
                  ]
                }
              ],
              "idShort": "TCFGoodsTransportAddressHandover",
              "modelType": "SubmodelElementCollection",
              "qualifiers": [
                {
                  "kind": "ConceptQualifier",
                  "type": "Cardinality",
                  "value": "One",
                  "valueType": "xs:string"
                }
              ],
              "semanticId": {
                "keys": [
                  {
                    "type": "GlobalReference",
                    "value": "0173-1#02-ABI498#001"
                  }
                ],
                "type": "ExternalReference"
              },
              "description": [
                {
                  "text": "Indicates the hand-over address of the goods transport ",
                  "language": "en"
                }
              ],
              "displayName": [
                {
                  "text": "Warenübergabeadresse für die Distributionsstufe",
                  "language": "de"
                },
                {
                  "text": "Goods transport address hand-over for distribution stage",
                  "language": "en"
                }
              ]
            },
            {
              "idShort": "PublicationDate",
              "category": "PARAMETER",
              "modelType": "Property",
              "valueType": "xs:string",
              "qualifiers": [
                {
                  "kind": "ConceptQualifier",
                  "type": "Cardinality",
                  "value": "One",
                  "valueType": "xs:string"
                }
              ],
              "semanticId": {
                "keys": [
                  {
                    "type": "GlobalReference",
                    "value": "https://admin-shell.io/idta/CarbonFootprint/PublicationDate/1/0"
                  }
                ],
                "type": "ExternalReference"
              },
              "description": [
                {
                  "text": "Time at which something was first published or made available",
                  "language": "en"
                }
              ],
              "displayName": [
                {
                  "text": "Veröffentlichungsdatum",
                  "language": "de"
                },
                {
                  "text": "Publication date",
                  "language": "en"
                }
              ]
            },
            {
              "idShort": "ExpirationDate",
              "category": "PARAMETER",
              "modelType": "Property",
              "valueType": "xs:string",
              "qualifiers": [
                {
                  "kind": "ConceptQualifier",
                  "type": "Cardinality",
                  "value": "ZeroToOne",
                  "valueType": "xs:string"
                }
              ],
              "semanticId": {
                "keys": [
                  {
                    "type": "GlobalReference",
                    "value": "https://admin-shell.io/idta/CarbonFootprint/ExpirationnDate/1/0"
                  }
                ],
                "type": "ExternalReference"
              },
              "description": [
                {
                  "text": "Time at which something should no longer be used effectively because it may lose its validity, quality or safety",
                  "language": "en"
                }
              ],
              "displayName": [
                {
                  "text": "Ablaufdatum",
                  "language": "de"
                },
                {
                  "text": "Expiration Date",
                  "language": "en"
                }
              ]
            }
          ],
          "idShort": "TransportCarbonFootprint",
          "modelType": "SubmodelElementCollection",
          "qualifiers": [
            {
              "kind": "ConceptQualifier",
              "type": "Cardinality",
              "value": "ZeroToMany",
              "valueType": "xs:string"
            }
          ],
          "semanticId": {
            "keys": [
              {
                "type": "GlobalReference",
                "value": "https://admin-shell.io/idta/CarbonFootprint/TransportCarbonFootprint/0/9"
              }
            ],
            "type": "ExternalReference"
          },
          "description": [
            {
              "text": "Balance of greenhouse gas emissions generated by a transport service of a product",
              "language": "en"
            }
          ],
          "displayName": [
            {
              "text": "Transport C02-Fußabdruck",
              "language": "de"
            },
            {
              "text": "Transport carbon footprint",
              "language": "en"
            }
          ]
        }
      ]
    },
{
  "idShort": "BillOfMaterials",
  "id": "https://example.com/ids/sm/9220_0192_5052_9397",
  "semanticId": {
    "type": "ModelReference",
    "keys": [
      {
        "type": "Submodel",
        "value": "http://example.com/semantic/BillOfMaterials"
      }
    ]
  },
  "submodelElements": [
    {
      "category": "CONSTANT",
      "idShort": "Vereinzeler",
      "value": [
        { "idShort": "Lagerung_Antriebsstange_Vereinzeler_(63370800)", "valueType": "xs:integer", "value": "2", "modelType": "Property", "link": "https://www.maedler.de/product/1643/3043/1899/gelenklager-din-12240-1-e-wartungsfrei" },
        { "idShort": "Kupplung_Vereinzeler_8mm_(60060800)", "valueType": "xs:integer", "value": "1", "modelType": "Property", "link": "https://www.maedler.de/product/1643/1622/1644/geschlitzte-schalenkupplungen-mas-stahl-ohne-nut" }
      ],
      "modelType": "SubmodelElementCollection"
    },
    {
      "category": "CONSTANT",
      "idShort": "Förderband",
      "value": [
        { "idShort": "Lagerung_Förderband", "valueType": "xs:integer", "value": "4", "modelType": "Property", "link": "https://www.maedler.de/Article/61800-ZZ-MAE" },
        { "idShort": "Kupplung_Förderband_8mm_(60060800)", "valueType": "xs:integer", "value": "1", "modelType": "Property", "link": "https://www.maedler.de/product/1643/1622/1644/geschlitzte-schalenkupplungen-mas-stahl-ohne-nut" }
      ],
      "modelType": "SubmodelElementCollection"
    },
    {
      "category": "CONSTANT",
      "idShort": "Entnahmeförderband",
      "value": [
        { "idShort": "Lagerung_Entnahmeförderband", "valueType": "xs:integer", "value": "4", "modelType": "Property", "link": "https://www.maedler.de/Article/61800-ZZ-MAE" },
        { "idShort": "Kupplung_Entnahmeförderband_8mm_(60060800)", "valueType": "xs:integer", "value": "1", "modelType": "Property", "link": "https://www.maedler.de/product/1643/1622/1644/geschlitzte-schalenkupplungen-mas-stahl-ohne-nut" }
      ],
      "modelType": "SubmodelElementCollection"
    },
    {
      "category": "CONSTANT",
      "idShort": "Trichterbunker",
      "value": [
        { "idShort": "Kupplung_Trichterbunker_8mm_(60060800)", "valueType": "xs:integer", "value": "1", "modelType": "Property", "link": "https://www.maedler.de/product/1643/1622/1644/geschlitzte-schalenkupplungen-mas-stahl-ohne-nut" }
      ],
      "modelType": "SubmodelElementCollection"
    },
    {
      "category": "CONSTANT",
      "idShort": "Profile_20x20mm",
      "value": [
        { "idShort": "Länge_410mm", "valueType": "xs:integer", "value": "7", "modelType": "Property" },
        { "idShort": "Länge_450mm", "valueType": "xs:integer", "value": "4", "modelType": "Property" },
        { "idShort": "Länge_255mm", "valueType": "xs:integer", "value": "4", "modelType": "Property" },
        { "idShort": "Länge_115mm", "valueType": "xs:integer", "value": "2", "modelType": "Property" },
        { "idShort": "Länge_140mm", "valueType": "xs:integer", "value": "3", "modelType": "Property" },
        { "idShort": "Länge_190mm", "valueType": "xs:integer", "value": "2", "modelType": "Property" },
        { "idShort": "Länge_150mm", "valueType": "xs:integer", "value": "4", "modelType": "Property" },
        { "idShort": "Länge_300mm", "valueType": "xs:integer", "value": "1", "modelType": "Property" },
        { "idShort": "Länge_380mm", "valueType": "xs:integer", "value": "2", "modelType": "Property" },
        { "idShort": "Länge_420mm", "valueType": "xs:integer", "value": "2", "modelType": "Property" },
        { "idShort": "Länge_520mm", "valueType": "xs:integer", "value": "2", "modelType": "Property" },
        { "idShort": "Länge_670mm", "valueType": "xs:integer", "value": "2", "modelType": "Property" },
        { "idShort": "Länge_175mm", "valueType": "xs:integer", "value": "1", "modelType": "Property" },
        { "idShort": "Länge_205mm", "valueType": "xs:integer", "value": "2", "modelType": "Property" },
        { "idShort": "Länge_160mm", "valueType": "xs:integer", "value": "1", "modelType": "Property" },
        { "idShort": "Länge_260mm", "valueType": "xs:integer", "value": "2", "modelType": "Property" },
        { "idShort": "Länge_210mm", "valueType": "xs:integer", "value": "1", "modelType": "Property" }
      ],
      "modelType": "SubmodelElementCollection"
    },
    {
      "category": "CONSTANT",
      "idShort": "Transportbänder",
      "value": [
        {
          "idShort": "Transportband_Schwarz_1,7mm_1575x83mm_endlos",
          "valueType": "xs:integer",
          "value": "1",
          "modelType": "Property"
        },
        {
          "idShort": "Transportband_Weiss_1,0mm_1255x59mm_endlos",
          "valueType": "xs:integer",
          "value": "1",
          "modelType": "Property"
        }
      ],
      "modelType": "SubmodelElementCollection"
    },
    {
      "category": "CONSTANT",
      "idShort": "Vereinzeler_Baugruppe",
      "value": [
        { "idShort": "Getriebemotor_Micromotors_(E192.24.5)", "valueType": "xs:integer", "value": "1", "modelType": "Property", "link": "https://www.reichelt.at/getriebemotor-40-5-mm-5-1-24-v-dc-gm40-5-5-24v-p159650.html?&trstct=pol_6&nbc=1" },
        { "idShort": "PWM_Leistungsregler_9-28VDC", "valueType": "xs:integer", "value": "1", "modelType": "Property", "link": "https://www.reichelt.de/pwm-leistungsregler-9-28vdc-10a-m-171-p119309.html" },
        { "idShort": "Sicherungshalter_5x20mm_10A_250V", "valueType": "xs:integer", "value": "1", "modelType": "Property", "link": "https://www.reichelt.de/sicherungshalter-5x20mm-max-10a-250v-pl-126001-p141971.html?&trstct=pos_0&nbc=1" },
        { "idShort": "Feinsicherung_5x20mm_träge_5A", "valueType": "xs:integer", "value": "1", "modelType": "Property", "link": "https://www.reichelt.de/feinsicherung-5x20mm-traege-5-a-litt-0218005-mxp-p241974.html?&trstct=pos_0&nbc=1" },
        { "idShort": "Relaissockel_FIN_40.51/.52/.61,_blau", "valueType": "xs:integer", "value": "1", "modelType": "Property", "link": "https://www.reichelt.at/relaissockel-fuer-fin-40-51-52-61-blau-fin-95-95-3-p26576.html?&trstct=pos_0&nbc=1" },
        { "idShort": "Steckrelais_2xUM_250V_8A_24V", "valueType": "xs:integer", "value": "1", "modelType": "Property", "link": "https://www.reichelt.at/steckrelais-2x-um-250v-8a-24v-rm-5-0mm-fin-40-52-9-24v-p8107.html?&trstct=pos_0" },
        { "idShort": "Lichtschranke_Sick_W4S-3_(WSE4SC-3P2230S04)", "valueType": "xs:integer", "value": "2", "modelType": "Property", "link": "https://www.sick.com/at/de/lichttaster-und-lichtschranken/lichttaster-und-lichtschranken/w4s-3/wse4sc-3p2230s04/p/p434348" },
        { "idShort": "Kabel_Lichtschranke_Empfänger_M8_M12", "valueType": "xs:integer", "value": "2", "modelType": "Property", "link": "https://www.sick.com/at/de/yf8u14-020ua3m2a14/p/p559388" },
        { "idShort": "Kabel_Lichtschranke_Sender_M8_LosesEnde", "valueType": "xs:integer", "value": "2", "modelType": "Property", "link": "https://www.sick.com/at/de/yf8u14-020va3xleax/p/p559217" }
      ],
      "modelType": "SubmodelElementCollection"
    },
    {
      "category": "CONSTANT",
      "idShort": "Förderband_Baugruppe",
      "value": [
        { "idShort": "Getriebemotor_Micromotors_(E192.24.49)", "valueType": "xs:integer", "value": "1", "modelType": "Property", "link": "https://at.rs-online.com/web/p/dc-getriebemotor/8777152/" },
        { "idShort": "PWM_Leistungsregler_9-28VDC", "valueType": "xs:integer", "value": "1", "modelType": "Property", "link": "https://www.reichelt.de/pwm-leistungsregler-9-28vdc-10a-m-171-p119309.html" },
        { "idShort": "Sicherungshalter_5x20mm_10A_250V", "valueType": "xs:integer", "value": "1", "modelType": "Property", "link": "https://www.reichelt.de/sicherungshalter-5x20mm-max-10a-250v-pl-126001-p141971.html?&trstct=pos_0&nbc=1" },
        { "idShort": "Feinsicherung_5x20mm_träge_5A", "valueType": "xs:integer", "value": "1", "modelType": "Property", "link": "https://www.reichelt.de/feinsicherung-5x20mm-traege-5-a-litt-0218005-mxp-p241974.html?&trstct=pos_0&nbc=1" },
        { "idShort": "Relaissockel_FIN_40.51/.52/.61,_blau", "valueType": "xs:integer", "value": "1", "modelType": "Property", "link": "https://www.reichelt.at/relaissockel-fuer-fin-40-51-52-61-blau-fin-95-95-3-p26576.html?&trstct=pos_0&nbc=1" },
        { "idShort": "Steckrelais_2xUM_250V_8A_24V", "valueType": "xs:integer", "value": "1", "modelType": "Property", "link": "https://www.reichelt.at/steckrelais-2x-um-250v-8a-24v-rm-5-0mm-fin-40-52-9-24v-p8107.html?&trstct=pos_0" },
        { "idShort": "Linearantrieb_SMC_LEYG16MB_100_S1CL18", "valueType": "xs:integer", "value": "1", "modelType": "Property", "link": "https://www.smc.eu/en-eu/products/leyg-guide-rod-type-step-motor-24v-dc~133959~cfg?partNumber=LEYG16MB-100-S1CL18" },
        { "idShort": "Kabel_Linearantrieb_M12_LosesEnde", "valueType": "xs:integer", "value": "1", "modelType": "Property", "link": "https://www.sick.com/at/de/ym2a14-020ub3xleax/p/p559447" },
        { "idShort": "Lichtschranke_Sick_W4S-3_(WSE4SC-3P2230S04)", "valueType": "xs:integer", "value": "1", "modelType": "Property", "link": "https://www.sick.com/at/de/lichttaster-und-lichtschranken/lichttaster-und-lichtschranken/w4s-3/wse4sc-3p2230s04/p/p434348" },
        { "idShort": "Kabel_Lichtschranke_Empfänger_M8_M12", "valueType": "xs:integer", "value": "1", "modelType": "Property", "link": "https://www.sick.com/at/de/yf8u14-020ua3m2a14/p/p559388" },
        { "idShort": "Kabel_Lichtschranke_Sender_M8_LosesEnde", "valueType": "xs:integer", "value": "1", "modelType": "Property", "link": "https://www.sick.com/at/de/yf8u14-020va3xleax/p/p559217" }
      ],
      "modelType": "SubmodelElementCollection"
    },
{
  "category": "CONSTANT",
  "idShort": "Entnahmeförderband_Baugruppe",
  "value": [
    { "idShort": "Getriebemotor_Micromotors_(E192.24.49)", "valueType": "xs:integer", "value": "1", "modelType": "Property", "link": "https://at.rs-online.com/web/p/dc-getriebemotor/8777152/" },
    { "idShort": "PWM_Leistungsregler_9-28VDC", "valueType": "xs:integer", "value": "1", "modelType": "Property", "link": "https://www.reichelt.de/pwm-leistungsregler-9-28vdc-10a-m-171-p119309.html" },
    { "idShort": "Sicherungshalter_5x20mm_10A_250V", "valueType": "xs:integer", "value": "1", "modelType": "Property", "link": "https://www.reichelt.de/sicherungshalter-5x20mm-max-10a-250v-pl-126001-p141971.html?&trstct=pos_0&nbc=1" },
    { "idShort": "Feinsicherung_5x20mm_träge_5A", "valueType": "xs:integer", "value": "1", "modelType": "Property", "link": "https://www.reichelt.de/feinsicherung-5x20mm-traege-5-a-litt-0218005-mxp-p241974.html?&trstct=pos_0&nbc=1" },
    { "idShort": "Relaissockel_FIN_40.51/.52/.61,_blau", "valueType": "xs:integer", "value": "1", "modelType": "Property", "link": "https://www.reichelt.at/relaissockel-fuer-fin-40-51-52-61-blau-fin-95-95-3-p26576.html?&trstct=pos_0&nbc=1" },
    { "idShort": "Steckrelais_2xUM_250V_8A_24V", "valueType": "xs:integer", "value": "1", "modelType": "Property", "link": "https://www.reichelt.at/steckrelais-2x-um-250v-8a-24v-rm-5-0mm-fin-40-52-9-24v-p8107.html?&trstct=pos_0" }
  ],
  "modelType": "SubmodelElementCollection"
},
{
  "category": "CONSTANT",
  "idShort": "Trichterbunker_Baugruppe",
  "value": [
    { "idShort": "Getriebemotor_Micromotors_(E192.24.336)", "valueType": "xs:integer", "value": "1", "modelType": "Property", "link": "https://www.reichelt.at/getriebemotor-40-5-mm-336-1-24-v-dc-gm40-5-336-24v-p159656.html?&trstct=pos_0&nbc=1" },
    { "idShort": "PWM_Leistungsregler_9-28VDC", "valueType": "xs:integer", "value": "1", "modelType": "Property", "link": "https://www.reichelt.de/pwm-leistungsregler-9-28vdc-10a-m-171-p119309.html" },
    { "idShort": "Sicherungshalter_5x20mm_10A_250V", "valueType": "xs:integer", "value": "1", "modelType": "Property", "link": "https://www.reichelt.de/sicherungshalter-5x20mm-max-10a-250v-pl-126001-p141971.html?&trstct=pos_0&nbc=1" },
    { "idShort": "Feinsicherung_5x20mm_träge_5A", "valueType": "xs:integer", "value": "1", "modelType": "Property", "link": "https://www.reichelt.de/feinsicherung-5x20mm-traege-5-a-litt-0218005-mxp-p241974.html?&trstct=pos_0&nbc=1" },
    { "idShort": "Relaissockel_FIN_40.51/.52/.61,_blau_(L:81,9/B:15,5/H:64,8mm)", "valueType": "xs:integer", "value": "2", "modelType": "Property", "link": "https://www.reichelt.at/relaissockel-fuer-fin-40-51-52-61-blau-fin-95-95-3-p26576.html?&trstct=pos_0&nbc=1" },
    { "idShort": "Steckrelais_2xUM_250V_8A_24V", "valueType": "xs:integer", "value": "2", "modelType": "Property", "link": "https://www.reichelt.at/steckrelais-2x-um-250v-8a-24v-rm-5-0mm-fin-40-52-9-24v-p8107.html?&trstct=pos_0" },
    { "idShort": "Linearantrieb_SMC-LEY16B-100-S1CL18", "valueType": "xs:integer", "value": "1", "modelType": "Property", "link": "https://www.smc.eu/en-eu/products/ley-rod-type-step-motor-24v-dc~133934~cfg?partNumber=LEY16B-100-S1CL18" },
    { "idShort": "Kabel_Linearantrieb_M12_LosesEnde", "valueType": "xs:integer", "value": "1", "modelType": "Property", "link": "https://www.sick.com/at/de/ym2a14-020ub3xleax/p/p559447" },
    { "idShort": "Absolut_Encoder_Sick_AHM36B-BBQC", "valueType": "xs:integer", "value": "1", "modelType": "Property", "link": "https://www.sick.com/at/de/encoder/absolut-encoder/ahsahm36/c/g543428" },
    { "idShort": "Kabel_Absolut_Encoder_M12_Dose/M12_Stecker", "valueType": "xs:integer", "value": "1", "modelType": "Property", "link": "https://www.sick.com/at/de/yf2a14-020ub3m2a14/p/p559345" }
  ],
  "modelType": "SubmodelElementCollection"
},
{
  "category": "CONSTANT",
  "idShort": "Steuerung_und_Zubehör",
  "value": [
    { "idShort": "NOT_AUS_Schalter_Tafelmontage", "valueType": "xs:integer", "value": "1", "modelType": "Property", "link": "https://at.rs-online.com/web/p/not-aus-schalter/6096164/" },
    { "idShort": "Drucktaster_2mm_Schwarz", "valueType": "xs:integer", "value": "3", "modelType": "Property", "link": "https://at.rs-online.com/web/p/drucktaster-komplettgerate/3308616/" },
    { "idShort": "SIEMENS_SIMATIC_S7_1200_CPU_1215C", "valueType": "xs:integer", "value": "1", "modelType": "Property", "link": "https://mall.industry.siemens.com/mall/de/WW/Catalog/Product/6ES7215-1AG40-0XB0" },
    { "idShort": "SICK_IO_Link_Master_SIG200", "valueType": "xs:integer", "value": "2", "modelType": "Property", "link": "https://www.sick.com/at/de/integrationsprodukte/sensor-integration-gateway/sig200/sig200-0a0412200/p/p653695" },
    { "idShort": "Kabel_SIG200_Siemens_M12_Stecker_D-kodiert/RJ45", "valueType": "xs:integer", "value": "1", "modelType": "Property", "link": "https://www.sick.com/at/de/ym2d24-020ea1mrja4/p/p314700" },
    { "idShort": "Kabel_SIG200_SIG200_M12_Stecker_D-kodiert", "valueType": "xs:integer", "value": "1", "modelType": "Property", "link": "https://www.sick.com/at/de/ym2d24-c50ea1m2d24/p/p314690" },
    { "idShort": "Kabel_SIG200_Netzteil_M12_Stecker_A-kodiert/LosesEnde", "valueType": "xs:integer", "value": "2", "modelType": "Property", "link": "https://www.sick.com/at/de/yf2a25-015ub6xleax/p/p559306" }
  ],
  "modelType": "SubmodelElementCollection"
},
{
  "category": "CONSTANT",
  "idShort": "Schaltschrank",
  "value": [
    {
      "idShort": "DIN_Hutschiene_7_5x35mm_L_500mm",
      "valueType": "xs:integer",
      "value": "1",
      "modelType": "Property",
      "link": "https://at.rs-online.com/web/p/din-schienen/0467406"
    },
    {
      "idShort": "Sicherungshalter_5x20mm_10A_250V",
      "valueType": "xs:integer",
      "value": "1",
      "modelType": "Property",
      "link": "https://www.reichelt.de/sicherungshalter-5x20mm-max-10a-250v-pl-126001-p141971.html?&trstct=pos_0&nbc=1"
    },
    {
      "idShort": "Feinsicherung_5x20mm_träge_10A",
      "valueType": "xs:integer",
      "value": "1",
      "modelType": "Property",
      "link": "https://at.rs-online.com/web/p/feinsicherungen/0563334/"
    },
    {
      "idShort": "Hauptschalter_beleuchtet",
      "valueType": "xs:integer",
      "value": "1",
      "modelType": "Property",
      "link": "https://at.rs-online.com/web/p/wippschalter/3779759/"
    },
    {
      "idShort": "Schukostecker_ABL_Sursum_Netz,_Stecker,_Frankreich,_Deutschland",
      "valueType": "xs:integer",
      "value": "1",
      "modelType": "Property",
      "link": "https://at.rs-online.com/web/p/netzstecker-und-steckdosen/0327169/"
    },
    {
      "idShort": "Netzwerkkabel_Cat5e_Patch",
      "valueType": "xs:integer",
      "value": "1",
      "modelType": "Property",
      "link": "https://at.rs-online.com/web/p/kat5e-kabel/0557032/"
    },
    {
      "idShort": "Reihenklemmen_0.2_→_2.5mm²_800V_24A_10erPack",
      "valueType": "xs:integer",
      "value": "2",
      "modelType": "Property",
      "link": "https://at.rs-online.com/web/p/anschlussklemmenblocke-fur-din-schienen/0501639/"
    }
  ],
  "modelType": "SubmodelElementCollection"
},
    {
      "category": "CONSTANT",
      "idShort": "QualityCheck",
      "value": [
        { "idShort": "SIM4000", "valueType": "xs:integer", "value": "1", "modelType": "Property", "link": "https://www.sick.com/at/de/sensor-integration-machine/sim4x00/sim4000-0p03g10/p/p451945" },
        { "idShort": "picoCam302x_Art._Nr._I2D302C-RCA11", "valueType": "xs:integer", "value": "2", "modelType": "Property", "link": "https://www.sick.com/de/de/industrielle-bildverarbeitung/2d-machine-vision/picocam/i2d302c-rca11/p/p446948" },
        { "idShort": "picoCam_Kabel_SIM4000_picoCam", "valueType": "xs:integer", "value": "2", "modelType": "Property", "link": "https://www.sick.com/de/de/ym2aa5-030ub6fhrs6/p/p459973" },
        { "idShort": "picoCam_Ethernet_Kabel", "valueType": "xs:integer", "value": "2", "modelType": "Property", "link": "https://www.sick.com/de/de/ym2x18-020eg2mrja8/p/p330046" },
        { "idShort": "Ringlicht_di_soric_BE-R30-G5-K-BS-DIF", "valueType": "xs:integer", "value": "2", "modelType": "Property", "link": "https://www.di-soric.com/int-de/PM/Bildverarbeitung-Identifikation/Beleuchtungen-fuer-Bildverarbeitung/BE-R-Ringbeleuchtungen/Ringbeleuchtungen-mit-schaltbarem-Gleichlicht/BE-R30-G5-K-BS-DIF__209555" },
        { "idShort": "Ringlicht_Kabel_SIM4000_Ringlicht", "valueType": "xs:integer", "value": "2", "modelType": "Property", "link": "https://www.sick.com/de/de/yf2a14-020ub3m2a14/p/p559345" },
        { "idShort": "WLAN_TP_Link", "valueType": "xs:integer", "value": "1", "modelType": "Property", "link": "https://www.tp-link.com/de/home-networking/wifi-router/tl-wr802n/" },
        { "idShort": "WLAN_Ethernet_Kabel_SIM4000_WLAN", "valueType": "xs:integer", "value": "1", "modelType": "Property", "link": "https://www.sick.com/de/de/ym2x18-020eg2mrja8/p/p330046" }
      ],
      "modelType": "SubmodelElementCollection"
    }
  ]
},
{
  "idShort": "EndOfLife",
  "category": "EoL",
  "modelType": "Submodel",
  "description": [
    {
      "language": "en",
      "text": "End-of-life handling of components for disassembly, disposal and recycling."
    },
    {
      "language": "de",
      "text": "End-of-Life Informationen zur Entsorgung und zum Recycling der Bauteile."
    }
  ],
  "submodelElements": [
    {
      "idShort": "Motoren",
      "modelType": "SubmodelElementCollection",
      "value": [
        {
          "idShort": "RS_877-7152_24Vdc_60RPM",
          "modelType": "Property",
          "valueType": "xs:string",
          "value": "Recycelbar über WEEE, Elektromotor → Metallverwertung"
        },
        {
          "idShort": "MicroMotors_E192.24.336",
          "modelType": "Property",
          "valueType": "xs:string",
          "value": "Elektronik-Sondermüll, Metallanteil recycelbar"
        },
        {
          "idShort": "SMC_LEY16B-100-S1CL18",
          "modelType": "Property",
          "valueType": "xs:string",
          "value": "Elektro-Altgerät, zurück zum Hersteller oder Metallrecycling"
        },
        {
          "idShort": "SMC_LEYG16MB-100-S1CL18",
          "modelType": "Property",
          "valueType": "xs:string",
          "value": "Elektro-Altgerät, Metall- & Elektronikrecycling"
        }
      ]
    },
    {
      "idShort": "Netzteile",
      "modelType": "SubmodelElementCollection",
      "value": [
        {
          "idShort": "Kemo_M171",
          "modelType": "Property",
          "valueType": "xs:string",
          "value": "Elektronikschrott, Platinen in E-Schrottcontainer"
        },
        {
          "idShort": "RND_315-00011_SU100",
          "modelType": "Property",
          "valueType": "xs:string",
          "value": "Elektronikschrott, recycelbar über WEEE"
        }
      ]
    },
    {
      "idShort": "IO-Links_Netzteile",
      "modelType": "SubmodelElementCollection",
      "value": [
        {
          "idShort": "SMC_JXCL18-LEY16B-100",
          "modelType": "Property",
          "valueType": "xs:string",
          "value": "Elektronikschrott (IO-Link), Recycling über E-Schrott"
        }
      ]
    },
    {
      "idShort": "Geraete",
      "modelType": "SubmodelElementCollection",
      "value": [
        {
          "idShort": "Siemens_S7-1200",
          "modelType": "Property",
          "valueType": "xs:string",
          "value": "Industrie-Steuerung → WEEE Recycling"
        },
        {
          "idShort": "SICK_SIG200",
          "modelType": "Property",
          "valueType": "xs:string",
          "value": "Elektronikschrott, Gewerblicher E-Waste Container"
        },
        {
          "idShort": "SICK_SIM4000",
          "modelType": "Property",
          "valueType": "xs:string",
          "value": "Elektronikschrott, WEEE Recycling"
        }
      ]
    },
    {
      "idShort": "Sensoren",
      "modelType": "SubmodelElementCollection",
      "value": [
        {
          "idShort": "SICK_WE4SC",
          "modelType": "Property",
          "valueType": "xs:string",
          "value": "Elektronikschrott, Sammelstelle für Sensoren/Platinen"
        }
      ]
    },
    {
      "idShort": "Relaissockel",
      "modelType": "SubmodelElementCollection",
      "value": [
        {
          "idShort": "Finder_95.95.3",
          "modelType": "Property",
          "valueType": "xs:string",
          "value": "Elektroschrott → Kleinmaterial, Metall und Kunststoff trennbar"
        },
        {
          "idShort": "RINA_40.52.9.024.000",
          "modelType": "Property",
          "valueType": "xs:string",
          "value": "Kunststoff + Metall, entsorgen über Elektronikschrott"
        }
      ]
    },
    {
      "idShort": "Bereitschaftsleuchte",
      "modelType": "SubmodelElementCollection",
      "value": [
        {
          "idShort": "WERMA_693.010.55_12VDC_IP65",
          "modelType": "Property",
          "valueType": "xs:string",
          "value": "Lampen Recycling Container → z. B. Gewerbliche Leuchten-Sammlung"
        }
      ]
    },
    {
      "idShort": "Encoder",
      "modelType": "SubmodelElementCollection",
      "value": [
        {
          "idShort": "SICK_AHM36B-BBQC012X12",
          "modelType": "Property",
          "valueType": "xs:string",
          "value": "Elektronik-Schrott, Metallkern recyceln"
        }
      ]
    },
    {
      "idShort": "Sicherungen",
      "modelType": "SubmodelElementCollection",
      "value": [
        {
          "idShort": "Littelfuse_218",
          "valueType": "xs:string",
          "modelType": "Property",
          "value": "Glas + Metall, Elektro-Sondermüll"
        },
        {
          "idShort": "Goobay_GSH135",
          "valueType": "xs:string",
          "modelType": "Property",
          "value": "Plastikgehäuse, Metall zurückgewinnen"
        }
      ]
    },
    {
      "idShort": "Router",
      "modelType": "SubmodelElementCollection",
      "value": [
        {
          "idShort": "TP-Link_TL-WR802N",
          "modelType": "Property",
          "valueType": "xs:string",
          "value": "Elektro-Kleingeräte Recycling → Router in E-Schrott geben"
        }
      ]
    },
    {
      "idShort": "Taster_Regler",
      "modelType": "SubmodelElementCollection",
      "value": [
        {
          "idShort": "SICK_NotAus",
          "modelType": "Property",
          "valueType": "xs:string",
          "value": "Sicherheitskomponente → Elektronikschrott"
        },
        {
          "idShort": "Metall_Drehregler",
          "modelType": "Property",
          "valueType": "xs:string",
          "value": "Metallverwertung"
        },
        {
          "idShort": "Taster_gross",
          "modelType": "Property",
          "valueType": "xs:string",
          "value": "Elektroschrott (Plastik+Kontakt)"
        },
        {
          "idShort": "Taster_gruen_klein",
          "modelType": "Property",
          "valueType": "xs:string",
          "value": "Elektroschrott, Kunststoffanteil"
        },
        {
          "idShort": "EinAus_Kippschalter",
          "modelType": "Property",
          "valueType": "xs:string",
          "value": "Elektroschrott"
        }
      ]
    },
    {
      "idShort": "MechanischeTeile",
      "modelType": "SubmodelElementCollection",
      "value": [
        {
          "idShort": "Holz",
          "valueType": "xs:string",
          "modelType": "Property",
          "value": "Restmüll oder Holzverwertung"
        },
        {
          "idShort": "Aluminium_Geruest_Rollen",
          "valueType": "xs:string",
          "modelType": "Property",
          "value": "Metallcontainer / Alu-Recycling"
        },
        {
          "idShort": "3D_Druck_Bauteile",
          "valueType": "xs:string",
          "modelType": "Property",
          "value": "Kunststoffrecycling oder Restmüll (PLA/ABS)"
        },
        {
          "idShort": "Plexiglas",
          "valueType": "xs:string",
          "modelType": "Property",
          "value": "Kunststoff-Sammlung oder Wertstoffhof"
        },
        {
          "idShort": "Kabelkanal_Plastik",
          "valueType": "xs:string",
          "modelType": "Property",
          "value": "Kunststoffverwertung"
        },
        {
          "idShort": "Förderbänder",
          "valueType": "xs:string",
          "modelType": "Property",
          "value": "Kunststoff + Textil → Restmüll oder Sonderverwertung"
        }
      ]
    }
  ]
}
  ],
  "assetAdministrationShells": [
    {
      "id": "https://example.com/ids/aas/8103_9092_5052_3109",
      "idShort": "Sortingmachine",
      "category": "PARAMETER",
      "modelType": "AssetAdministrationShell",
      "submodels": [
        {
          "keys": [
            {
              "type": "Submodel",
              "value": "https://example.com/ids/sm/6283_9092_5052_7177"
            }
          ],
          "type": "ModelReference"
        },
        {
          "keys": [
            {
              "type": "Submodel",
              "value": "https://example.com/ids/sm/9220_0192_5052_9396"
            }
          ],
          "type": "ModelReference"
        },
        {
          "keys": [
            {
              "type": "Submodel",
              "value": "https://admin-shell.io/idta/SubmodelTemplate/CarbonFootprint/0/9"
            }
          ],
          "type": "ModelReference"
        }
      ],
      "derivedFrom": {
        "keys": [
          {
            "type": "AssetAdministrationShell",
            "value": ""
          }
        ],
        "type": "ModelReference"
      },
      "displayName": [
        {
          "text": "Mechatronical Sorting Machine",
          "language": "en"
        },
        {
          "text": "Mechatronische Sortiermaschine",
          "language": "de"
        }
      ],
      "assetInformation": {
        "assetKind": "NotApplicable",
        "assetType": "",
        "globalAssetId": "https://example.com/ids/asset/7184_9092_5052_0603",
        "defaultThumbnail": {
          "path": "files/images/IMG_20250418_092401224.jpg"
        },
        "specificAssetIds": []
      }
    }
  ]
}

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# PostgreSQL Verbindung

db_config = {
    'host': os.getenv("DB_HOST", "db"),
    'port': int(os.getenv("DB_PORT", 5432)),
    'database': os.getenv("DB_NAME", "postgres"),
    'user': os.getenv("DB_USER", "postgres"),
    'password': os.getenv("DB_PASSWORD", "postgres")
}

def get_conn():
    return psycopg2.connect(**db_config)

def init_db():
    """Erstellt Tabellen falls nicht vorhanden"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS product_passes (
            id SERIAL PRIMARY KEY,
            json_data JSONB NOT NULL
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id SERIAL PRIMARY KEY,
            product_pass_id INTEGER REFERENCES product_passes(id) ON DELETE CASCADE,
            name TEXT,
            filename TEXT,
            mimetype TEXT,
            content BYTEA
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

@app.post("/product_pass")
async def upload_product_pass(json_data: str = Form(...)):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO product_passes (json_data) VALUES (%s) RETURNING id;", (json_data,))
    pid = cur.fetchone()[0]
    conn.commit(); cur.close(); conn.close()
    return {"ok": True, "product_pass_id": pid}


@app.get("/product_pass/{pid}")
def get_product_pass(pid: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT json_data FROM product_passes WHERE id=%s;", (pid,))
    row = cur.fetchone()
    cur.close(); conn.close()
    if row:
        content = row[0]
        if isinstance(content, str):
            content = json.loads(content)
        return JSONResponse(content=content)
    raise HTTPException(status_code=404, detail="Nicht gefunden")


@app.get("/product_passes")
def list_product_passes(limit: int = 20):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, json_data FROM product_passes ORDER BY id DESC LIMIT %s;", (limit,))
    rows = cur.fetchall()
    cur.close(); conn.close()
    result = []
    for rid, jdata in rows:
        if isinstance(jdata, str):
            jdata = json.loads(jdata)
        result.append({"id": rid, "data": jdata})
    return result

@app.post("/documents")
async def upload_document(
    product_pass_id: int = Form(...),
    name: str = Form(...),
    file: UploadFile = File(...)
):
    content = await file.read()
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO documents (product_pass_id, name, filename, mimetype, content)
        VALUES (%s, %s, %s, %s, %s) RETURNING id;
    """, (product_pass_id, name, file.filename, file.content_type, content))
    did = cur.fetchone()[0]
    conn.commit(); cur.close(); conn.close()
    return {"ok": True, "document_id": did}


@app.get("/documents/{did}")
def get_document(did: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT filename, mimetype, content FROM documents WHERE id=%s;", (did,))
    row = cur.fetchone()
    cur.close(); conn.close()
    if row:
        return StreamingResponse(
            io.BytesIO(row[2]),
            media_type=row[1],
            headers={"Content-Disposition": f"inline; filename={row[0]}"}
        )
    raise HTTPException(status_code=404, detail="Nicht gefunden")

if not os.path.exists("files"):
    os.makedirs("files")

app.mount("/files", StaticFiles(directory="files"), name="files")

@app.post("/uploadfile/")
async def upload_file(file: UploadFile = File(...)):
    filepath = os.path.join("files", file.filename)
    with open(filepath, "wb") as buffer:
        buffer.write(await file.read())
    return {"filename": file.filename, "url": f"/files/{file.filename}"}

@app.get("/files/{filename}")
async def get_file(filename: str):
    filepath = os.path.join("files", filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(filepath)

# Simulation

sim_running = False
sim_thread = None
sim_start_real = None
sim_start_virtual = None
SIM_FACTOR = 3000  # 1 reale Sekunde = 3000 sek simulierte Zeit


def vary(v, delta):
    """zufällige kleine Variation um ±delta/2"""
    return round(v + (random.random() - 0.5) * delta, 2)


def simulation_loop():
    global sim_running, sim_start_real, sim_start_virtual

    if sim_start_real is None:
        sim_start_real = datetime.utcnow()
        sim_start_virtual = datetime(2025, 1, 1, 8, 0, 0)

    print("Simulation gestartet...")

    while sim_running:
        dpp = copy.deepcopy(base_template)

        # eindeutige ID
        ts = str(int(time.time() * 1000))
        dpp["assetAdministrationShells"][0]["id"] = "shell-" + ts

        # simulierte Zeit berechnen
        elapsed_real = (datetime.utcnow() - sim_start_real).total_seconds()
        simulated_time = sim_start_virtual + timedelta(seconds=elapsed_real * SIM_FACTOR)

        # Carbon Footprint zufällig variieren
        cf_submodel = next((sm for sm in dpp["submodels"] if sm.get("idShort") == "CarbonFootprint"), None)
        if cf_submodel:
            cf_phase_element = next((el for el in cf_submodel.get("submodelElements", [])
                                    if el.get("idShort") == "CFPhases"), None)
            if cf_phase_element:
                cf = cf_phase_element["value"]["phases"]
                cf["A1"] = vary(float(cf["A1"]), 2)
                cf["A2"] = vary(float(cf["A2"]), 0.3)
                cf["A3"] = vary(float(cf["A3"]), 0.5)
                cf["A4"] = round(float(cf["A4"]) + random.uniform(0.1, 0.5), 2)
        else:
            cf = None

        # Produktionszeit hinzufügen
        prod_time = {
            "value": simulated_time.isoformat() + "Z",
            "idShort": "ProductionDateTime",
            "category": "PARAMETER",
            "modelType": "Property",
            "valueType": "xs:dateTime"
        }

        nameplate = next((sm for sm in dpp["submodels"] if sm.get("idShort") == "Nameplate"), None)
        if nameplate:
            nameplate.setdefault("submodelElements", []).append(prod_time)
        else:
            dpp["submodels"].append({"idShort": "Nameplate", "submodelElements": [prod_time]})

        # Daten in DB speichern
        try:
            conn = get_conn()
            cur = conn.cursor()
            cur.execute("INSERT INTO product_passes (json_data) VALUES (%s) RETURNING id;", (json.dumps(dpp),))
            pid = cur.fetchone()[0]
            conn.commit(); cur.close(); conn.close()
            print(f"Neues DPP gespeichert: {pid} | SimZeit: {simulated_time.isoformat()} | CF: {cf}")
        except Exception as e:
            print("Fehler beim Insert:", e)

        time.sleep(5)

# Simulation Endpoints

@app.post("/start_simulation")
def start_simulation():
    global sim_running, sim_thread
    if sim_running:
        return {"status": "already running"}
    sim_running = True
    sim_thread = threading.Thread(target=simulation_loop, daemon=True)
    sim_thread.start()
    return {"status": "started"}


@app.post("/stop_simulation")
def stop_simulation():
    global sim_running
    sim_running = False
    return {"status": "stopped"}


@app.get("/simulation_status")
def simulation_status():
    return {"running": sim_running}

@app.on_event("startup")
def startup_event():
    init_db()
    print("Datenbank initialisiert, Simulation bereit.")