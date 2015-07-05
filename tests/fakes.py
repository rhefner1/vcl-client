ENDPOINT = 'http://abc.com/endpoint.php'

USERNAME = 'user'

PASSWORD = 'password'

JSON_RETURN = '[{"ID": 123, "Name": "test"}]'

XML_RETURN = """<?xml version="1.0" encoding="iso-8859-1"?>
<methodResponse>
<params>
 <param>
  <value>
   <struct>
    <member>
     <name>status</name>
     <value>
      <string>success</string>
     </value>
    </member>
    <member>
     <name>requests</name>
     <value>
      <array>
       <data/>
      </array>
     </value>
    </member>
   </struct>
  </value>
 </param>
</params>
</methodResponse>
"""

XML_PARSED = {'status': 'success', 'requests': []}
