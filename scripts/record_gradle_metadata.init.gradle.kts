// Dependency-update helper: run after resolving only this project in an isolated
// Gradle user home. Normal CI never writes verification metadata.
import javax.xml.parsers.DocumentBuilderFactory

gradle.projectsEvaluated {
    val root = rootProject
    root.tasks.register("recordResolvedPomChecksums") {
        doLast {
            val metadata = root.file("gradle/verification-metadata.xml")
            val document = DocumentBuilderFactory.newInstance().newDocumentBuilder().parse(metadata)
            val known = mutableSetOf<String>()
            val components = document.getElementsByTagName("component")
            for (i in 0 until components.length) {
                val component = components.item(i) as org.w3c.dom.Element
                val artifacts = component.getElementsByTagName("artifact")
                if ((0 until artifacts.length).any { (artifacts.item(it) as org.w3c.dom.Element).getAttribute("name").endsWith(".pom") }) {
                    known.add("${component.getAttribute("group")}:${component.getAttribute("name")}:${component.getAttribute("version")}")
                }
            }
            val cache = gradle.gradleUserHomeDir.resolve("caches/modules-2/files-2.1")
            val localRepository = root.file(".gradle/resolved-pom-repository")
            // Preserve original Gradle-cached POM bytes; no hand-written checksums.
            for (pom in cache.walkTopDown().filter { it.isFile && it.extension == "pom" }.toList()) {
                val parts = pom.relativeTo(cache).invariantSeparatorsPath.split('/')
                val sha1 = java.security.MessageDigest.getInstance("SHA-1").digest(pom.readBytes()).joinToString("") { "%02x".format(it) }
                check(sha1.trimStart('0') == pom.parentFile.name.trimStart('0')) { "Corrupt Gradle POM cache: $pom" }
                val target = localRepository.resolve(parts[0].replace('.', '/')+"/${parts[1]}/${parts[2]}/${pom.name}")
                target.parentFile.mkdirs()
                check(!target.exists() || target.readBytes().contentEquals(pom.readBytes())) { "Different POM bytes for ${pom.name}" }
                pom.copyTo(target, overwrite=true)
            }
            root.repositories.clear()
            root.repositories.maven { url = root.uri(localRepository) }
            var added = 0
            for (pom in cache.walkTopDown().filter { it.isFile && it.extension == "pom" }.toList()) {
                val parts = pom.relativeTo(cache).invariantSeparatorsPath.split('/')
                val coordinate = "${parts[0]}:${parts[1]}:${parts[2]}"
                if (coordinate in known) continue
                println("Resolving transient metadata $coordinate")
                val dependency = root.dependencies.create("$coordinate@pom")
                val configuration = root.configurations.detachedConfiguration(dependency)
                configuration.isTransitive = false
                configuration.resolve()
                added++
                known.add(coordinate)
            }
            println("Recorded $added additional resolved POM artifacts, including transient parents/BOMs")
        }
    }
}
