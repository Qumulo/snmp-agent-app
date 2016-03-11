#
# PySNMP MIB module QUMULO-MIB (http://pysnmp.sf.net)
# ASN.1 source file:///Users/mmurray/projects/qumulo/samples/snmp_agent/QUMULO-MIB
# Produced by pysmi-0.0.6 at Fri Mar 11 15:01:01 2016
# On host mmurrayMBP platform Darwin version 14.5.0 by user mmurray
# Using Python version 2.7.10 (default, Jun  1 2015, 09:44:56) 
#
( Integer, ObjectIdentifier, OctetString, ) = mibBuilder.importSymbols("ASN1", "Integer", "ObjectIdentifier", "OctetString")
( NamedValues, ) = mibBuilder.importSymbols("ASN1-ENUMERATION", "NamedValues")
( ConstraintsUnion, SingleValueConstraint, ConstraintsIntersection, ValueSizeConstraint, ValueRangeConstraint, ) = mibBuilder.importSymbols("ASN1-REFINEMENT", "ConstraintsUnion", "SingleValueConstraint", "ConstraintsIntersection", "ValueSizeConstraint", "ValueRangeConstraint")
( NotificationGroup, ModuleCompliance, ) = mibBuilder.importSymbols("SNMPv2-CONF", "NotificationGroup", "ModuleCompliance")
( Integer32, MibScalar, MibTable, MibTableRow, MibTableColumn, NotificationType, MibIdentifier, IpAddress, TimeTicks, Counter64, Unsigned32, enterprises, ModuleIdentity, Gauge32, iso, ObjectIdentity, Bits, Counter32, ) = mibBuilder.importSymbols("SNMPv2-SMI", "Integer32", "MibScalar", "MibTable", "MibTableRow", "MibTableColumn", "NotificationType", "MibIdentifier", "IpAddress", "TimeTicks", "Counter64", "Unsigned32", "enterprises", "ModuleIdentity", "Gauge32", "iso", "ObjectIdentity", "Bits", "Counter32")
( DisplayString, TextualConvention, ) = mibBuilder.importSymbols("SNMPv2-TC", "DisplayString", "TextualConvention")
qumuloModule = ModuleIdentity((47017, 2)).setRevisions(("2004-06-15 00:00", "2002-02-06 00:00",))
myCompany = MibIdentifier((1, 3, 6, 1, 4, 1, 47017))
testCount = MibScalar((1, 3, 6, 1, 4, 1, 47017, 1), Integer32()).setMaxAccess("readonly")
testDescription = MibScalar((1, 3, 6, 1, 4, 1, 47017, 2), OctetString()).setMaxAccess("readonly")
nodeDownTrap = NotificationType((1, 3, 6, 1, 4, 1, 47017, 3)).setObjects(*())
driveFailureTrap = NotificationType((1, 3, 6, 1, 4, 1, 47017, 4)).setObjects(*())
nodesClearTrap = NotificationType((1, 3, 6, 1, 4, 1, 47017, 5)).setObjects(*())
clusterUnreachableTrap = NotificationType((1, 3, 6, 1, 4, 1, 47017, 6)).setObjects(*())
powerSupplyFailureTrap = NotificationType((1, 3, 6, 1, 4, 1, 47017, 7)).setObjects(*())
nodeName = MibScalar((1, 3, 6, 1, 4, 1, 47017, 8), OctetString()).setMaxAccess("readonly")
driveId = MibScalar((1, 3, 6, 1, 4, 1, 47017, 9), OctetString()).setMaxAccess("readonly")
clusterName = MibScalar((1, 3, 6, 1, 4, 1, 47017, 10), OctetString()).setMaxAccess("readonly")
powerSupplyId = MibScalar((1, 3, 6, 1, 4, 1, 47017, 11), OctetString()).setMaxAccess("readonly")
mibBuilder.exportSymbols("QUMULO-MIB", testCount=testCount, clusterName=clusterName, nodesClearTrap=nodesClearTrap, driveFailureTrap=driveFailureTrap, testDescription=testDescription, nodeDownTrap=nodeDownTrap, driveId=driveId, clusterUnreachableTrap=clusterUnreachableTrap, powerSupplyId=powerSupplyId, qumuloModule=qumuloModule, PYSNMP_MODULE_ID=qumuloModule, nodeName=nodeName, myCompany=myCompany, powerSupplyFailureTrap=powerSupplyFailureTrap)
