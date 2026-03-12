package main

var (
	msgTimeSvcStart = [...]byte{'T', 'I', 'M', 'E', 'S', 'V', 'C', ':', ' ', 's', 't', 'a', 'r', 't', '\n'}
	msgTimeSvcReady = [...]byte{'T', 'I', 'M', 'E', 'S', 'V', 'C', ':', ' ', 'r', 'e', 'a', 'd', 'y', '\n'}
	msgTimeSvcReq   = [...]byte{'T', 'I', 'M', 'E', 'S', 'V', 'C', ':', ' ', 'r', 'e', 'q', ' ', 'o', 'k', '\n'}
	msgTimeSvcTime  = [...]byte{'T', 'I', 'M', 'E', 'S', 'V', 'C', ':', ' ', 't', 'i', 'm', 'e', ' ', 'o', 'k', '\n'}
	msgTimeSvcErr   = [...]byte{'T', 'I', 'M', 'E', 'S', 'V', 'C', ':', ' ', 'e', 'r', 'r', '\n'}

	msgShellStart     = [...]byte{'G', 'O', 'S', 'H', ':', ' ', 's', 't', 'a', 'r', 't', '\n'}
	msgShellRecycle   = [...]byte{'G', 'O', 'S', 'H', ':', ' ', 'r', 'e', 'c', 'y', 'c', 'l', 'e', '\n'}
	msgShellLookup    = [...]byte{'G', 'O', 'S', 'H', ':', ' ', 'l', 'o', 'o', 'k', 'u', 'p', ' ', 'o', 'k', '\n'}
	msgShellRecvDeny  = [...]byte{'G', 'O', 'S', 'H', ':', ' ', 'r', 'e', 'c', 'v', ' ', 'd', 'e', 'n', 'y', '\n'}
	msgShellRegDeny   = [...]byte{'G', 'O', 'S', 'H', ':', ' ', 'r', 'e', 'g', ' ', 'd', 'e', 'n', 'y', '\n'}
	msgShellSpawnDeny = [...]byte{'G', 'O', 'S', 'H', ':', ' ', 's', 'p', 'a', 'w', 'n', ' ', 'd', 'e', 'n', 'y', '\n'}
	msgShellReply     = [...]byte{'G', 'O', 'S', 'H', ':', ' ', 'r', 'e', 'p', 'l', 'y', ' ', 'o', 'k', '\n'}
	msgShellErr       = [...]byte{'G', 'O', 'S', 'H', ':', ' ', 'e', 'r', 'r', '\n'}
)

func timeServiceMain() {
	log(msgTimeSvcStart[:])

	serviceEP := sysIpcEndpointCreate()
	if serviceEP == sysErr {
		setServiceState(serviceTime, stateFailed)
		fail(msgTimeSvcErr[:])
	}
	if sysSvcRegister(&nameTimeSvc[0], uintptr(len(nameTimeSvc)), serviceEP) == sysErr {
		setServiceState(serviceTime, stateFailed)
		fail(msgTimeSvcErr[:])
	}

	setServiceState(serviceTime, stateRunning)
	log(msgTimeSvcReady[:])

	for bootFailed == 0 {
		var req [8]byte
		n := sysIpcRecv(serviceEP, &req[0], uintptr(len(req)))
		if n == sysErr {
			setServiceState(serviceTime, stateFailed)
			fail(msgTimeSvcErr[:])
		}
		if n == 1 && req[0] == cmdStop {
			break
		}
		if n != 2 || req[0] != cmdTime {
			setServiceState(serviceTime, stateFailed)
			fail(msgTimeSvcErr[:])
		}
		log(msgTimeSvcReq[:])

		if sysTimeNow() == sysErr {
			setServiceState(serviceTime, stateFailed)
			fail(msgTimeSvcErr[:])
		}
		log(msgTimeSvcTime[:])

		if sysIpcSend(uintptr(req[1]), &replyOK[0], uintptr(len(replyOK))) == sysErr {
			setServiceState(serviceTime, stateFailed)
			fail(msgTimeSvcErr[:])
		}
	}

	setServiceState(serviceTime, stateStopping)
	setServiceState(serviceTime, stateStopped)
	sysThreadExit()
	fail(msgTimeSvcErr[:])
}

func shellMain() {
	log(msgShellStart[:])

	if shellRecycles < 2 {
		shellRecycles++
		setServiceState(serviceShell, stateRunning)
		log(msgShellRecycle[:])
		sysThreadExit()
		fail(msgShellErr[:])
	}

	serviceEP := sysSvcLookup(&nameTimeSvc[0], uintptr(len(nameTimeSvc)))
	if serviceEP == sysErr {
		setServiceState(serviceShell, stateFailed)
		fail(msgShellErr[:])
	}
	log(msgShellLookup[:])

	var deny [1]byte
	if sysIpcRecv(serviceEP, &deny[0], uintptr(len(deny))) != sysErr {
		setServiceState(serviceShell, stateFailed)
		fail(msgShellErr[:])
	}
	log(msgShellRecvDeny[:])

	if sysSvcRegister(&nameHijack[0], uintptr(len(nameHijack)), serviceEP) != sysErr {
		setServiceState(serviceShell, stateFailed)
		fail(msgShellErr[:])
	}
	log(msgShellRegDeny[:])

	if sysThreadSpawn(spawnEntry) != sysErr {
		setServiceState(serviceShell, stateFailed)
		fail(msgShellErr[:])
	}
	log(msgShellSpawnDeny[:])

	replyEP := sysIpcEndpointCreate()
	if replyEP == sysErr {
		setServiceState(serviceShell, stateFailed)
		fail(msgShellErr[:])
	}

	setServiceState(serviceShell, stateRunning)

	req := [2]byte{cmdTime, byte(replyEP)}
	if sysIpcSend(serviceEP, &req[0], uintptr(len(req))) == sysErr {
		setServiceState(serviceShell, stateFailed)
		fail(msgShellErr[:])
	}

	var reply [4]byte
	n := sysIpcRecv(replyEP, &reply[0], uintptr(len(reply)))
	if n != uintptr(len(replyOK)) || reply[0] != replyOK[0] || reply[1] != replyOK[1] {
		setServiceState(serviceShell, stateFailed)
		fail(msgShellErr[:])
	}
	log(msgShellReply[:])

	stopReq := [1]byte{cmdStop}
	if sysIpcSend(serviceEP, &stopReq[0], uintptr(len(stopReq))) == sysErr {
		setServiceState(serviceShell, stateFailed)
		fail(msgShellErr[:])
	}

	setServiceState(serviceShell, stateStopping)
	shellComplete = 1
	setServiceState(serviceShell, stateStopped)
	sysThreadExit()
	fail(msgShellErr[:])
}
