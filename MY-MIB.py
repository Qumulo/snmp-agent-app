#
# PySNMP MIB module MY-MIB (http://pysnmp.sf.net)
# ASN.1 source file:///Users/mmurray/projects/qumulo/samples/snmp_agent/MY-MIB
# Produced by pysmi-0.0.6 at Fri Jan  8 15:19:48 2016
# On host mmurrayMBP platform Darwin version 14.5.0 by user mmurray
# Using Python version 2.7.10 (default, Jun  1 2015, 09:44:56) 
#
( Integer, ObjectIdentifier, OctetString, ) = mibBuilder.importSymbols("ASN1", "Integer", "ObjectIdentifier", "OctetString")
( NamedValues, ) = mibBuilder.importSymbols("ASN1-ENUMERATION", "NamedValues")
( ConstraintsUnion, SingleValueConstraint, ConstraintsIntersection, ValueSizeConstraint, ValueRangeConstraint, ) = mibBuilder.importSymbols("ASN1-REFINEMENT", "ConstraintsUnion", "SingleValueConstraint", "ConstraintsIntersection", "ValueSizeConstraint", "ValueRangeConstraint")
( NotificationGroup, ModuleCompliance, ) = mibBuilder.importSymbols("SNMPv2-CONF", "NotificationGroup", "ModuleCompliance")
( Integer32, MibScalar, MibTable, MibTableRow, MibTableColumn, NotificationType, MibIdentifier, IpAddress, TimeTicks, Counter64, Unsigned32, enterprises, iso, Gauge32, ModuleIdentity, ObjectIdentity, Bits, Counter32, ) = mibBuilder.importSymbols("SNMPv2-SMI", "Integer32", "MibScalar", "MibTable", "MibTableRow", "MibTableColumn", "NotificationType", "MibIdentifier", "IpAddress", "TimeTicks", "Counter64", "Unsigned32", "enterprises", "iso", "Gauge32", "ModuleIdentity", "ObjectIdentity", "Bits", "Counter32")
( DisplayString, TextualConvention, ) = mibBuilder.importSymbols("SNMPv2-TC", "DisplayString", "TextualConvention")
myCompany = MibIdentifier((1, 3, 6, 1, 4, 1, 43))
testCount = MibScalar((1, 3, 6, 1, 4, 1, 43, 1), Integer32()).setMaxAccess("readonly")
testDescription = MibScalar((1, 3, 6, 1, 4, 1, 43, 2), OctetString()).setMaxAccess("readonly")
nodeDownTrap = NotificationType((1, 3, 6, 1, 4, 1, 43, 3)).setObjects(*())
nodesClearTrap = NotificationType((1, 3, 6, 1, 4, 1, 43, 4)).setObjects(*())
nodeName = MibScalar((1, 3, 6, 1, 4, 1, 43, 5), DisplayString().subtype(subtypeSpec=ValueSizeConstraint(0,255))).setMaxAccess("readwrite")
mibBuilder.exportSymbols("MY-MIB", testCount=testCount, nodesClearTrap=nodesClearTrap, testDescription=testDescription, nodeDownTrap=nodeDownTrap, nodeName=nodeName, myCompany=myCompany)
