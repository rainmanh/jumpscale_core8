from JumpScale import j 
import os

with open("hrdtest.hrd", 'w') as f:
    f.writelines(["tok1 = \"sawerfgkjbnqerbgzaRGSRTGBER:Aefrvwejltrnbsd:fbj;kwfbs\"\n", 
                  "tok2 = \'sertgjnehrea:aerlghnqetrhq4haergtgq:rgearjgasrhgqwrger\'\n", 
                  "tok3 = \"edsrfvkwejhstbrgdzarbgasetbafbdfvadrgss:adFBGSALEKRBGAFVA\", \"AESKRJFHBAERVASERFAWEFQE:LWEJHKRBGARVAwerghw:Aerfa\"\n",
                  "tok4 = \'aerlgvhwbetrbgdzsjktrnaseFGSDTL:TEG:GESRGArgaergjwenrgkwf\', \'arelgiiwbenrgkajdnrgae:arewfgiwerbgsearbgzsdawefrg\'\n",
                  ]) 
hrddata = j.data.hrd.get("hrdtest.hrd") 
print(hrddata.getList("tok1"))#['sawerfgkjbnqerbgzaRGSRTGBER:Aefrvwejltrnbsd:fbj;kwfbs']
print(hrddata.getList("tok2"))#['sertgjnehrea:aerlghnqetrhq4haergtgq:rgearjgasrhgqwrger']
print(hrddata.getList("tok3"))#['edsrfvkwejhstbrgdzarbgasetbafbdfvadrgss:adFBGSALEKRBGAFVA', 'AESKRJFHBAERVASERFAWEFQE:LWEJHKRBGARVAwerghw:Aerfa']
print(hrddata.getList("tok4"))#['aerlgvhwbetrbgdzsjktrnaseFGSDTL:TEG:GESRGArgaergjwenrgkwf', 'arelgiiwbenrgkajdnrgae:arewfgiwerbgsearbgzsdawefrg']

os.remove("hrdtest.hrd")
#this shuold print 
#['sawerfgkjbnqerbgzaRGSRTGBER:Aefrvwejltrnbsd:fbj;kwfbs']
#['sertgjnehrea:aerlghnqetrhq4haergtgq:rgearjgasrhgqwrger']
#['edsrfvkwejhstbrgdzarbgasetbafbdfvadrgss:adFBGSALEKRBGAFVA', 'AESKRJFHBAERVASERFAWEFQE:LWEJHKRBGARVAwerghw:Aerfa']
#['aerlgvhwbetrbgdzsjktrnaseFGSDTL:TEG:GESRGArgaergjwenrgkwf', 'arelgiiwbenrgkajdnrgae:arewfgiwerbgsearbgzsdawefrg']
