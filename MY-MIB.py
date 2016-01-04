#
# PySNMP MIB module MY-MIB (http://pysnmp.sf.net)
# ASN.1 source file:///Users/mmurray/projects/qumulo/samples/snmp/MY-MIB
# Produced by pysmi-0.0.6 at Mon Jan  4 13:50:24 2016
# On host mmurrayMBP platform Darwin version 14.5.0 by user mmurray
# Using Python version 2.7.10 (default, Jun  1 2015, 09:44:56) 
#
( Integer, ObjectIdentifier, OctetString, ) = mibBuilder.importSymbols("ASN1", "Integer", "ObjectIdentifier", "OctetString")
( NamedValues, ) = mibBuilder.importSymbols("ASN1-ENUMERATION", "NamedValues")
( ConstraintsUnion, SingleValueConstraint, ConstraintsIntersection, ValueSizeConstraint, ValueRangeConstraint, ) = mibBuilder.importSymbols("ASN1-REFINEMENT", "ConstraintsUnion", "SingleValueConstraint", "ConstraintsIntersection", "ValueSizeConstraint", "ValueRangeConstraint")
( NotificationGroup, ModuleCompliance, ) = mibBuilder.importSymbols("SNMPv2-CONF", "NotificationGroup", "ModuleCompliance")
( Integer32, MibScalar, MibTable, MibTableRow, MibTableColumn, NotificationType, MibIdentifier, IpAddress, TimeTicks, Counter64, Unsigned32, enterprises, iso, Gauge32, ModuleIdentity, ObjectIdentity, Bits, Counter32, ) = mibBuilder.importSymbols("SNMPv2-SMI", "Integer32", "MibScalar", "MibTable", "MibTableRow", "MibTableColumn", "NotificationType", "MibIdentifier", "IpAddress", "TimeTicks", "Counter64", "Unsigned32", "enterprises", "iso", "Gauge32", "ModuleIdentity", "ObjectIdentity", "Bits", "Counter32")
( DisplayString, TextualConvention, ) = mibBuilder.importSymbols("SNMPv2-TC", "DisplayString", "TextualConvention")
myCompany = MibIdentifier((1, 3, 6, 1, 4, 1, 42))
testCount = MibScalar((1, 3, 6, 1, 4, 1, 42, 1), Integer32()).setMaxAccess("readonly")
testDescription = MibScalar((1, 3, 6, 1, 4, 1, 42, 2), OctetString()).setMaxAccess("readonly")
testTrap = NotificationType((1, 3, 6, 1, 4, 1, 42, 3)).setObjects(*())
mibBuilder.exportSymbols("MY-MIB", testCount=testCount, testDescription=testDescription, myCompany=myCompany, testTrap=testTrap)
